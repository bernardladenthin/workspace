# Code Writing Guide — Production Sources — Java 21 (supplement)

> **Versioned guide chain.** This file **extends**
> [`CODE_WRITING_GUIDE-8.md`](CODE_WRITING_GUIDE-8.md). All rules in
> the baseline apply unless an entry below explicitly overrides them.
> Read `-8.md` first, then this file.
>
> | File | Applies to | Inherits from |
> |---|---|---|
> | [`CODE_WRITING_GUIDE-8.md`](CODE_WRITING_GUIDE-8.md) | every sibling Java repo | — (baseline) |
> | [`CODE_WRITING_GUIDE-21.md`](CODE_WRITING_GUIDE-21.md) (this file) | `BitcoinAddressFinder` only | `-8.md` |
>
> **Eligibility.** Applies to repos whose `pom.xml` has
> `<release>16</release>` or later (records require Java 16+). Today
> only `BitcoinAddressFinder` (`<source>21</source>/<target>21</target>`)
> qualifies. `streambuffer`, `java-llama.cpp`, and
> `srcmorph` target Java 8 (`<release>8</release>`)
> and MUST NOT use the idioms below.
>
> **When BAF upgrades to a newer LTS** (Java 25 / 29 / ...): add
> `CODE_WRITING_GUIDE-<NEW>.md` next to this file with the same
> "extends previous" header. Do not modify older guide versions.

---

## 1. Records for Immutable Value Objects

Java `record` types are the preferred representation for immutable data
carriers in Java-16+ repos. Use records when:

- The class holds only final fields that are set at construction.
- There is no mutable state.
- The class has value semantics (equality based on field values).

```java
// GOOD — immutable value object as a record
public record KeyUtility(Network network, ByteBufferUtility byteBufferUtility) {
    // compact constructor allowed for validation
    public KeyUtility {
        Objects.requireNonNull(network, "network");
        Objects.requireNonNull(byteBufferUtility, "byteBufferUtility");
    }
}

// BAD — mutable class with getters/setters for a simple data carrier
public class KeyUtility {
    private Network network;
    public Network getNetwork() { return network; }
    public void setNetwork(Network network) { this.network = network; }
}
```

Verified in BAF: `KeyUtility`, `AddressToCoin`, `OpenCLDevice`, etc.
(5 records as of the last audit).

### Exception — framework-reflected POJOs

Classes instantiated by a framework via reflection (Jackson
deserialising JSON config in BAF, Maven `@Parameter`-bearing
configuration classes in the plugin) must remain regular classes with
setters or public fields, because the framework cannot inject values
into record components.

BAF's C-prefixed POJOs (`CProducerJava`, `CKeyProducerJavaRandom`,
etc.) are populated by Jackson and stay as classes for this reason.

---

## 2. Switch Expressions (arrow form)

Prefer switch expressions over `if`/`else if` chains and over the
legacy `switch` statement with fall-through.

```java
// GOOD — expression form, exhaustive, no fall-through
final NetworkParameters params = switch (chain) {
    case MAINNET -> MainNetParams.get();
    case TESTNET -> TestNet3Params.get();
    case REGTEST -> RegTestParams.get();
};

// GOOD — yield for multi-statement arms
final String label = switch (event.type()) {
    case CREATE -> "created";
    case UPDATE -> "updated";
    case DELETE -> {
        cleanupQueue.add(event.id());
        yield "deleted";
    }
};
```

Verified in BAF: `cli/Main.run` (commit `27c2ace` migrated
`if`/`else if` to arrow-form switch); `KeyProducerJavaRandom`
(commit `2cdfcc5` uses expression-form with `yield`).

Rules:

- Use the arrow form (`case X -> ...`) — never the colon form with
  fall-through.
- Cover every case (compiler enforces exhaustiveness on `enum` and
  sealed types).
- Throw `IllegalStateException` for the impossible default case rather
  than returning a sentinel value.

---

## 3. Text Blocks

Use text blocks for multi-line string literals — JSON, SQL,
HTML/Markdown, multi-line log messages, multi-line OpenCL kernel
fragments embedded in Java source.

```java
// GOOD — text block
private static final String EXAMPLE_CONFIG = """
        {
          "command": "Find",
          "finder": {
            "producers": [
              { "producerJava": { "threads": 8 } }
            ]
          }
        }
        """;

// BAD — string concatenation with explicit \n
private static final String EXAMPLE_CONFIG =
        "{\n"
        + "  \"command\": \"Find\",\n"
        + "  ...\n"
        + "}";
```

Rules:

- The opening `"""` must be followed by a newline; no content on the
  first line.
- Indentation is stripped to the minimum-common-leading-whitespace of
  all non-blank lines.
- Use `\s` to mark significant trailing whitespace when needed.

---

## 4. Pattern Matching for `instanceof`

Use pattern matching to combine the type check with the cast.

```java
// GOOD
if (obj instanceof Foo foo) {
    return foo.value();
}

// BAD — redundant cast
if (obj instanceof Foo) {
    Foo foo = (Foo) obj;
    return foo.value();
}
```

Verified in BAF: `Pair.equals` and similar `equals` overrides migrated
to `instanceof` pattern to satisfy Error Prone's `EqualsGetClass` rule.

---

## 5. `var` for Local Variables

Use `var` for local variables when the type is obvious from the
initializer and the code is clearer for it. Do NOT use `var` when:

- The right-hand side returns a generic type that's harder to read
  without the explicit declaration (`var list = new ArrayList<>();`
  is bad — it's `ArrayList<Object>`).
- The variable is initialised to `null` or a literal where the inferred
  type might be unexpected.
- The variable is a public field, method parameter, or method return
  type — `var` is local-only.

```java
// GOOD — type is obvious
var addresses = new ArrayList<Hash160>();
var consumer = new ConsumerJava(config, lookup, network);

// BAD — inferred type is wrong or unclear
var x = null;
var list = new ArrayList<>();
```

This rule is not strictly enforced; use judgement.

---

## 6. Sealed Types (when applicable)

For closed hierarchies (enum-like classes that need fields/methods, or
result types like "success or failure"), use `sealed` / `non-sealed`
to restrict subtypes. Pairs well with exhaustive switch expressions.

```java
public sealed interface LookupResult
        permits LookupResult.Hit, LookupResult.Miss {

    record Hit(Hash160 address, Coin amount) implements LookupResult {}
    record Miss() implements LookupResult {}
}

// Exhaustive switch over the sealed hierarchy:
return switch (result) {
    case LookupResult.Hit hit -> formatHit(hit);
    case LookupResult.Miss miss -> "not found";
};
```

No current BAF usage; documented here so the pattern is available when
a future closed hierarchy needs it.

---

## Out of scope for now

These Java-21+ features are intentionally not part of this supplement
until there's a real use case in the BAF codebase:

- **Virtual threads (`Thread.ofVirtual()`)** — BAF's producer-consumer
  uses platform threads via `ExecutorService` deliberately; virtual
  threads would change the cost model of `LinkedBlockingQueue` waits
  and need benchmarking before adoption.
- **Structured concurrency (`StructuredTaskScope`)** — preview API as
  of JDK 21; revisit when GA.
- **Foreign Function & Memory API** — relevant for any future direct
  native-memory work, but BAF currently uses LWJGL (its own `MemoryStack` /
  `MemoryUtil` off-heap allocators) for GPU memory.
