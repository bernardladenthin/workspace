# Test Writing Guide — Test Sources — Java 21 (supplement)

> **Versioned guide chain.** This file **extends**
> [`TEST_WRITING_GUIDE-8.md`](TEST_WRITING_GUIDE-8.md). All rules in
> the baseline apply unless an entry below explicitly overrides them.
> Read `-8.md` first, then this file.
>
> | File | Applies to | Inherits from |
> |---|---|---|
> | [`TEST_WRITING_GUIDE-8.md`](TEST_WRITING_GUIDE-8.md) | every sibling Java repo | — (baseline) |
> | [`TEST_WRITING_GUIDE-21.md`](TEST_WRITING_GUIDE-21.md) (this file) | `BitcoinAddressFinder` only | `-8.md` |
>
> **Eligibility.** Applies to repos whose test sources compile with
> `<release>16</release>` or later. Today only `BitcoinAddressFinder`
> qualifies.

---

## 1. Records for test fixtures

Use records for ad-hoc test data carriers (parameterized-test argument
groups, expected/actual pairs, complex test inputs). They eliminate
the boilerplate of writing `toString()` / `equals()` / `hashCode()` on
test-only POJOs.

```java
// GOOD — record as test fixture
private record Case(BigInteger input, BigInteger expected, String label) {}

static Stream<Case> killBitsArguments() {
    return Stream.of(
            new Case(BigInteger.ONE,     BigInteger.ONE,                 "single bit"),
            new Case(BigInteger.valueOf(8), BigInteger.valueOf(255L),    "byte boundary")
    );
}

@ParameterizedTest(name = "{0}")
@MethodSource("killBitsArguments")
public void getKillBits_parameterised_returnsExpected(Case c) {
    assertThat(bitHelper.getKillBits(c.input().intValue()), is(equalTo(c.expected())));
}
```

The Java 8 baseline pattern of returning `Arguments.of(...)` still
works in Java 21; records are a cleaner alternative when the same
argument shape appears in many tests in the same class.

---

## 2. Pattern matching in test assertions

Use pattern matching for `instanceof` in test code that needs to
unwrap a polymorphic result before asserting:

```java
// GOOD — pattern match + extraction in one expression
final LookupResult result = lookup.find(addr);
if (result instanceof LookupResult.Hit hit) {
    assertThat(hit.amount(), is(equalTo(Coin.valueOf(42))));
} else {
    fail("expected Hit, got " + result);
}
```

For sealed result types, prefer an exhaustive switch expression in
the assertion — the compiler then enforces that every arm is tested:

```java
final String summary = switch (result) {
    case LookupResult.Hit hit -> "hit:" + hit.amount();
    case LookupResult.Miss miss -> "miss";
};
assertThat(summary, is(equalTo("hit:42")));
```

---

## 3. Text blocks for fixture JSON / YAML / Markdown

Multi-line string literals in tests (expected JSON output, fixture
config files, sample documents) should use text blocks rather than
string concatenation with embedded `\n`:

```java
// GOOD — text block
private static final String EXPECTED_JSON = """
        {
          "command": "Find",
          "finder": {
            "producers": []
          }
        }
        """;

// BAD — concatenation
private static final String EXPECTED_JSON =
        "{\n"
        + "  \"command\": \"Find\",\n"
        + "  ...\n"
        + "}";
```

Be careful with indentation: text blocks strip the minimum-common-
leading-whitespace, which is rarely the indentation level you want
when comparing against actual program output. Use `.trim()` /
`.strip()` or write the expected value flush-left if exact whitespace
matters.

---

## 4. `var` for verbose test locals

Use `var` in tests when the right-hand side already makes the type
obvious — typical examples are mock setups, builder chains, and
collected lists. Same restrictions as in production code (see
`../src/CODE_WRITING_GUIDE-21.md` §5): no `var x = null`, no
`var list = new ArrayList<>()` with empty diamond.

```java
// GOOD
var captor = ArgumentCaptor.forClass(String.class);
var producer = new ProducerJava(config, keyUtility, bitHelper);

// BAD — inferred type is wrong / unclear
var x = mock.someMethod();  // what's the return type?
```

---

## 5. What does NOT belong here

These Java-21+ features are intentionally not part of this supplement
until they earn a use case in real test code:

- Virtual threads — tests should remain deterministic; do not introduce
  `Thread.ofVirtual()` to "speed up" a test suite.
- Structured concurrency (`StructuredTaskScope`) — preview API; not
  suitable for production tests yet.
- Foreign Function & Memory API — relevant only if a test is exercising
  native interop directly (very rare for Java tests).
