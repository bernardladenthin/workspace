# Code Writing Guide — Production Sources — Java 8 (baseline)

> **Versioned guide chain.** Files in this directory follow the naming
> convention `CODE_WRITING_GUIDE-<JAVA-VERSION>.md`. A higher-version
> file inherits all rules from every lower-version file in the chain
> and may add new rules or override individual rules from below.
> Read every file from the lowest applicable version up to the highest
> one your repo's `pom.xml` `<release>` allows.
>
> | File | Applies to | Inherits from |
> |---|---|---|
> | [`CODE_WRITING_GUIDE-8.md`](CODE_WRITING_GUIDE-8.md) (this file) | every sibling Java repo | — (baseline) |
> | [`CODE_WRITING_GUIDE-21.md`](CODE_WRITING_GUIDE-21.md) | `BitcoinAddressFinder` only (Java 21) | `-8.md` |
>
> When a repo upgrades to a new LTS, add a new
> `CODE_WRITING_GUIDE-<NEW>.md` file rather than editing older ones.
> Old files keep working for repos that have not upgraded.
>
> **This file (Java 8 baseline):** applies to every sibling Java repo
> (`BitcoinAddressFinder`, `java-llama.cpp`,
> `srcmorph`, `streambuffer`). Three of the four
> build to Java 8 bytecode (`<release>8</release>` in `pom.xml`); BAF
> targets Java 21 but still follows everything below.
>
> Each repo's own `CODE_WRITING_GUIDE.md` (if present) contains only
> **project-specific supplements** — not version-related rules.
>
> For TDD workflow see
> [`../../.claude/skills/java-tdd-guide/SKILL.md`](../../.claude/skills/java-tdd-guide/SKILL.md).

---

## 1. Named Constants — DRY, No Inline Literals

The primary motivation is **Don't Repeat Yourself (DRY)**. Every
meaningful value must exist in exactly **one** authoritative place — a
named constant — so that a future change requires editing only one line.

### Rules

- Every string, number, or flag literal that carries semantic meaning
  **must** be a named `public static final` or `private static final`
  constant. Inline magic values are **prohibited**.
- Constants must be placed at the top of the class, before constructors
  and methods.
- The name must describe the **meaning or role** of the value, not the
  value itself.
- Each constant **must** have a Javadoc comment that explains what the
  value represents and why it has that specific value.
- When a derived value is needed, define **both** the source constant
  and the derived constant, and compute the derived one from the
  source — never duplicate the raw literal.

```java
// BAD — magic literals inline
if (name.endsWith(".ai.md")) { ... }
header.put("h", "1.0");

// GOOD — one authoritative constant with Javadoc
/**
 * File extension appended to every source file name to produce its
 * AI index file name. Example: "MyClass.java" -> "MyClass.java.ai.md".
 */
public static final String AI_MD_EXTENSION = ".ai.md";
```

Verified adoption: BAF has 141 `static final` declarations across 29
production source files.

Repo-specific applications (BAF's `BitHelper.RADIX_*`, the plugin's
header-field-key / node-type / provider-name constants) live in each
repo's own supplement.

---

## 2. Custom Domain Exceptions

Throw a specific named exception type rather than generic
`IllegalArgumentException` / `RuntimeException` when a domain meaning is
involved. Domain exceptions document the failure mode at the throw site
and let callers catch the specific case they can handle.

Verified in BAF: `KeyProducerIdNullException`,
`KeyProducerIdIsNotUniqueException`, `KeyProducerIdUnknownException`,
`NoMoreSecretsAvailableException`, `PrivateKeyTooLargeException`,
`UnknownSecretFormatException`, `AddressFormatNotAcceptedException`.

```java
// BAD — what's actually wrong here?
throw new IllegalArgumentException("bad key");

// GOOD — name documents the failure mode
throw new PrivateKeyTooLargeException("private key " + key + " exceeds secp256k1 range");
```

`IllegalArgumentException` is still appropriate for truly generic
constraint failures with no domain meaning (e.g. "argument must be
non-negative" for a public utility method).

---

## 3. Constructor Injection — Dependencies and Configuration

Dependencies and configuration arrive through the constructor with
`private final` fields. This makes the dependency graph explicit and
lets tests substitute fakes without touching production code.

```java
public class ProducerJava {

    private final CProducerJava config;
    private final KeyUtility keyUtility;
    private final BitHelper bitHelper;

    public ProducerJava(
            CProducerJava config,
            KeyUtility keyUtility,
            BitHelper bitHelper) {
        this.config = config;
        this.keyUtility = keyUtility;
        this.bitHelper = bitHelper;
    }
}
```

### Loggers — two valid patterns

**SLF4J static-field idiom** (used in BAF, jllama, streambuffer):

```java
private static final Logger LOG = LoggerFactory.getLogger(Foo.class);
```

In tests, capture log output with **LogCaptor** rather than mocking the
static field. This is the idiom that's actually in production across
the SLF4J-using repos.

**Maven `Log` constructor injection** (used in the plugin, applicable
only to Mojo collaborators):

```java
public SourceFileIndexer(final Log log, ...) {
    this.log = log;
}
```

The plugin uses constructor-injected `Log` because Mojos receive their
logger from `AbstractMojo.getLog()` and pass it down. SLF4J repos do
not follow this pattern and do not need to.

---

## 4. Defensive Null and Empty Checks at Public Boundaries

Validate `null` and empty inputs at the entry point of every public
method that would otherwise propagate a `NullPointerException` deep
into a call stack.

- Prefer `log.warn(...)` + early return over silent skips for cases
  that indicate a misconfiguration.
- Throw `IllegalArgumentException` (or the appropriate domain exception)
  with a descriptive message for programming errors.

```java
// GOOD — clear error for unsupported configuration
throw new IllegalArgumentException("Unsupported field target: " + target);

// GOOD — warn and skip rather than silently doing nothing
if (!Files.exists(sourceFile)) {
    log.warn("Skipping missing source file: " + sourceFile);
    return false;
}
```

With NullAway in strict JSpecify mode (enabled in every sibling repo),
the implicit non-null default removes most boundary checks at compile
time. This rule applies to input edges NullAway cannot prove safe —
JSON-deserialised values, file/network input, reflection-populated
fields.

---

## 5. Helper Classes — Instance Methods Over Static Utilities

Helper classes should be designed for mockability and testability.

### Rules

- Prefer instance methods over static methods.
- Helper classes must be regular classes (not `final`), with instance
  methods (not `static`).
- No private constructor — allow normal object creation.
- Store an instance as a field in classes that use the helper, making
  the dependency explicit and injectable.

### When static methods ARE acceptable

- Pure mathematical functions with no side effects;
- Trivial string/number formatting that never needs to be mocked;
- Constant lookup functions that have no external dependencies.

### Example — BAF migration

```java
// BAD — static utility, not mockable
public final class KeyUtility {
    private KeyUtility() { }
    public static boolean isInvalidWithBatchSize(BigInteger key, BigInteger max) { ... }
}

// GOOD — instance method on a dedicated validator
public class PrivateKeyValidator {
    public boolean isInvalidWithBatchSize(BigInteger key, BigInteger max) { ... }
}

public class ProducerJava {
    private final PrivateKeyValidator validator = new PrivateKeyValidator();
    // ...
}
```

Verified in BAF: `PrivateKeyValidator.getMaxPrivateKeyForBatchSize` /
`isInvalidWithBatchSize` / `isOutsidePrivateKeyRange` / etc. moved off
the `KeyUtility` static surface.

---

## 6. `@VisibleForTesting`

Use the Guava annotation
(`com.google.common.annotations.VisibleForTesting`) to mark
package-private or protected members that exist only so tests can reach
them. The annotation is documentation, not enforcement; it signals
intent to readers and to static-analysis tools.

`@VisibleForTesting` should be the last resort, not the first. Before
applying it, check whether constructor injection, behaviour extraction,
or making the observable property a public method achieves the same
goal without widening visibility. See
[`../../policies/code-quality-todos.md`](../../policies/code-quality-todos.md)
for the design-fit review.

Verified in BAF: 16 sites across 5 production files. The other three
sibling repos have zero usages.

---

## 7. License Headers — SPDX Form

Every source file across every sibling repo must include the SPDX-format
license header:

<!-- REUSE-IgnoreStart -->
```java
// SPDX-FileCopyrightText: <YEAR-RANGE> Bernard Ladenthin <bernard.ladenthin@gmail.com>
//
// SPDX-License-Identifier: Apache-2.0
package net.ladenthin.<repo>;
```

Rules:

- Three single-line comments — no `/* ... */` block.
- No `// @formatter:off` / `// @formatter:on` wrapper. The SPDX form
  does not need formatter exemption (the canonical guide previously
  said otherwise — that was wrong; verified by `grep` returning 2 hits
  in 1 file across the entire fleet).
- `<YEAR-RANGE>` is the file's actual lifespan (e.g. `2017-2026`,
  `2014-2026`), not the current year.
- License identifier is **Apache-2.0** in BAF, sb, and plugin.
  `java-llama.cpp` uses **MIT** with a dual-copyright line for the
  upstream Konstantin Herud attribution:

  ```java
  // SPDX-FileCopyrightText: 2023 Konstantin Herud
  // SPDX-FileCopyrightText: 2024-2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
  //
  // SPDX-License-Identifier: MIT
  ```

<!-- REUSE-IgnoreEnd -->

REUSE-tool compliance is enforced via the `reuse.yml` GitHub workflow
in every repo.

---

## 8. Concurrency

- Use `LinkedBlockingQueue<byte[]>` (or similar `java.util.concurrent`
  primitives) for producer-consumer hand-off.
- Use `ExecutorService` / `ThreadPoolExecutor` for thread pool
  management. **Do not introduce raw `Thread` usage** — ArchUnit rules
  in every repo enforce this (`no Thread.sleep` in production code).
- Use `AtomicLong` / `AtomicBoolean` / `AtomicInteger` for thread-safe
  flags and counters.
- Use `CountDownLatch` for shutdown synchronization.

Repo-specific shutdown contracts (BAF's `Interruptable`, streambuffer's
`bufferLock` + `Semaphore signalModification`) live in the per-repo
supplements.

---

## What's NOT in this canonical guide and why

- **Records.** Java 16+ feature; only BAF can use them today. See the
  Java 21 supplement.
- **Switch expressions, text blocks, pattern matching.** Same reason;
  see the Java 21 supplement.
- **Key-indexed definition pattern** (`AiPromptDefinition` /
  `AiPromptSupport`). Used only by the plugin; lives in the plugin's
  own supplement.
- **Constructor-injected Maven `Log`.** Plugin-only; documented in
  §3 above as one of two valid logger patterns.
