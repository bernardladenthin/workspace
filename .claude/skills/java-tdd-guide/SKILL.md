---
name: java-tdd-guide
description: Bernard Ladenthin's personal Java Test-Driven Development skill — Red → Green → Refactor workflow with project-independent conventions. Baselines on Java 8 + JUnit Jupiter; BAF-specific Java 21 idioms live in the optional supplement.
---

# Java TDD Skill — Test-Driven Development

**Author:** Bernard Ladenthin
**License:** MIT OR Apache-2.0

This is the canonical Java TDD skill for the four sibling repos
(`BitcoinAddressFinder`, `streambuffer`, `java-llama.cpp`,
`srcmorph`, formerly `llamacpp-ai-index-maven-plugin`). It describes the workflow and
conventions that are **actually in use** across the codebases — verified
by reading the test sources, not invented.

**Baseline assumed by this skill:** Java 8 + JUnit Jupiter 6.1.x +
Hamcrest 3.0 (exact versions live in the canonical tool-version matrix in
`workspace/crossrepostatus.md`; they are deliberately not re-pinned here). Java 21 idioms (records, switch expressions, text blocks)
are documented separately in
[`../../../guides/src/CODE_WRITING_GUIDE-21.md`](../../../guides/src/CODE_WRITING_GUIDE-21.md);
only `BitcoinAddressFinder` targets Java 21 today.

---

## TDD Workflow — Red → Green → Refactor

Follow the **Red → Green → Refactor** cycle rigorously. Every new
behaviour must be covered by a failing test *before* the production code
is written.

### 1 — Red (failing test first)

Write one test that precisely describes the next desired behaviour. The
test must compile but **must fail** when run. Do not write any production
code yet.

### 2 — Green (minimum production code)

Write the smallest change to production code that makes the failing test
pass. Do not add code that is not driven by a test.

### 3 — Refactor

Improve the implementation and the test code without changing observable
behaviour. All tests must stay green.

Repeat for each behaviour increment.

---

## Test Framework — the actually-used stack

| Concern | Choice | Evidence |
|---|---|---|
| Runner | **JUnit Jupiter** 6.1.x (`org.junit.jupiter.api.*`) | `pom.xml` in all four repos; exact version in `crossrepostatus.md` |
| Assertions | **Hamcrest 3.0** (`assertThat(actual, is(equalTo(expected)))`) | universally adopted; `assertThrows` is the one Jupiter assertion that's always allowed |
| Parameterized | `@ParameterizedTest` + `@MethodSource(SourceClass.CONSTANT_NAME)` | `BitHelperTest.java:21,33`; `StreamBufferTest.java:42-47` |
| Mocking | **Mockito** (`mock()`, `when()`, `verify()`, `ArgumentCaptor`) | BAF + plugin; not used by sb/jllama |
| Temp filesystem | `@TempDir Path folder` (JUnit Jupiter native) | universal |
| Property-based (optional) | jqwik **pinned ≤ 1.9.3** | see policies/jqwik-prompt-injection.md |

**Never use:**

- `org.junit.Test` / `org.junit.Before` / `org.junit.Rule` (JUnit 4) — banned via Maven Enforcer
- `@RunWith(DataProviderRunner.class)` + `com.tngtech.java.junit.dataprovider` — **not used in any repo**
- TestNG
- `assertEquals` etc. from `org.junit.jupiter.api.Assertions` when Hamcrest can express it more clearly. Two narrow exceptions are accepted in practice and visible in `StreamBufferTest`: (a) `assertThrows`/`assertDoesNotThrow` for exception assertion, (b) `assertArrayEquals` when comparing byte arrays.

---

## Test File Structure

### File header — SPDX

Every test file **must** start with the SPDX-format license header:

<!-- REUSE-IgnoreStart -->
```java
// SPDX-FileCopyrightText: <YEAR-RANGE> Bernard Ladenthin <bernard.ladenthin@gmail.com>
//
// SPDX-License-Identifier: Apache-2.0
package net.ladenthin.<repo>;
```

- `<YEAR-RANGE>` is the file's actual lifespan (e.g. `2017-2026`,
  `2014-2026`).
- No `// @formatter:off` / `// @formatter:on` wrapper — the SPDX block
  is three single-line comments and does not need formatter exemption.
- jllama uses MIT (`SPDX-License-Identifier: MIT`) with a dual-copyright
  line for the upstream Konstantin Herud attribution; everywhere else
  is Apache-2.0.

<!-- REUSE-IgnoreEnd -->

### Class declaration

```java
public class FooTest {
```

No runner annotation — JUnit Jupiter auto-discovers `@Test` /
`@ParameterizedTest` methods.

---

## Two equally valid grouping styles

Owner's actual codebases use two different patterns to group related
tests within a class. **Both are accepted** in workspace canonical; pick
the style that matches the surrounding file rather than mixing.

### Style A — NetBeans `<editor-fold>` (used in BAF, plugin)

```java
// <editor-fold defaultstate="collapsed" desc="getKillBits">
@ParameterizedTest
@MethodSource(CommonDataProvider.DATA_PROVIDER_KILL_BITS)
public void getKillBits_bitsGiven_killBitsEqualsExpectation(int bits, BigInteger killBits) {
    // ...
}
// </editor-fold>
```

Rules: `desc` equals the method name (or a short feature label);
`defaultstate="collapsed"` is mandatory; one fold per method under test.

### Style B — `@Nested` + `@DisplayName` (used in streambuffer)

```java
@Nested
@DisplayName("roundtrip")
class RoundtripTests {
    @DisplayName("simple round trip")
    @Test
    public void testSimpleRoundTrip() throws IOException {
        // ...
    }
}
```

Rules: each `@Nested` class groups tests for a related behaviour;
`@DisplayName` provides the human-readable label.

The two styles are not interchangeable inside one class. Stay consistent
within a file.

---

## Test Method Naming

Pattern: **`methodUnderTest_inputOrCondition_expectedBehavior`**

```
getKillBits_bitsGiven_killBitsEqualsExpectation
convertBitsToSize_bitsGiven_sizeEqualsExpectation
assertBatchSizeInBitsIsInRange_bitsGivenBelowMinimum_exceptionThrown
```

Verified in BAF: `BitHelperTest.java:22,34,45,54,66`.

Rules:

- All three segments are **required** and separated by underscores.
- Use camelCase within each segment.
- The `expected` segment describes the observable outcome
  (`_returnsZero`, `_throwsException`, `_exceptionThrown`,
  `_skipsFile`, `_roundtripsCorrectly`).
- Exception tests end with `_throwsException` or `_exceptionThrown`.
- No-op / smoke tests use `_noExceptionThrown`.

Inside `@Nested` classes (streambuffer style), naming may relax to
`testFoo` because `@DisplayName` provides the readable label; do not
mix the relaxed naming into a non-`@Nested` class.

---

## Test Body — AAA Structure

Every test body **must** follow the Arrange / Act / Assert structure
with explicit section comments. Verified in BAF (323+ matches across 10
files), sb (658 matches in one file), plugin (129 matches). The combined
`// act, assert` comma form is acceptable when the act IS the assertion
(`BitHelperTest.java:26,38,49,58,70`):

```java
@Test
public void getKillBits_bitsGiven_killBitsEqualsExpectation(int bits, BigInteger killBits) {
    // arrange
    BitHelper bitHelper = new BitHelper();

    // act, assert
    assertThat(bitHelper.getKillBits(bits), is(equalTo(killBits)));
}
```

For separate act + assert:

```java
@Test
public void example() {
    // arrange
    Foo foo = new Foo();

    // act
    int result = foo.doThing();

    // assert
    assertThat(result, is(equalTo(42)));
}
```

### `// pre-assert` — two valid positions

`// pre-assert` is a named section that asserts a condition without it
being the primary assertion of the test. Use it (a) before `// act` to
verify a precondition, or (b) between `// act` and `// assert` as a
null-guard before accessing fields.

```java
// act
final Foo result = sut.compute();

// pre-assert
assertThat(result, is(notNullValue()));

// assert
assertThat(result.value(), is(equalTo("expected")));
```

Rules:

- `// arrange` may be omitted only when there is genuinely nothing to
  arrange.
- Keep the act to a **single method call** whenever possible.
- Do **not** use `Objects.requireNonNull(...)` as a guard in tests; use
  a `// pre-assert` with `assertThat(x, is(notNullValue()))`.

---

## Assertions — Hamcrest Style

```java
// equality
assertThat(result, is(equalTo(expected)));

// null / not null
assertThat(result, is(nullValue()));
assertThat(result, is(notNullValue()));

// boolean
assertThat(flag, is(true));
assertThat(flag, is(false));

// negation
assertThat(result, is(not(equalTo(unexpected))));

// strings
assertThat(message, containsString("substring"));
assertThat(output, not(emptyOrNullString()));

// collections
assertThat(list, hasSize(3));
assertThat(list, is(empty()));

// numbers
assertThat(count, is(greaterThan(0)));
```

**Imports to use:**

```java
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
// or specific:
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
```

Two narrow exceptions where Jupiter assertions are acceptable:

```java
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;  // byte-array compare
```

---

## Exception Testing

```java
@Test
public void doIt_invalidInput_throwsException() {
    // arrange
    Foo foo = new Foo();

    // act, assert
    assertThrows(IllegalArgumentException.class, () -> foo.doIt(-1));
}

// With message check:
@Test
public void doIt_invalidInput_throwsExceptionWithReason() {
    // arrange
    Foo foo = new Foo();

    // act
    IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
            () -> foo.doIt(-1));

    // assert
    assertThat(e.getMessage(), containsString("must be >= 0"));
}
```

Verified in BAF `BitHelperTest.java:50,59`.

---

## Parameterized Tests — `@MethodSource`

The owner's pattern stores method-source names as named string constants
on a `CommonDataProvider` (or sibling provider) class, then references
them symbolically from `@MethodSource`. This prevents typos and makes
provider methods easy to find via "find usages".

```java
// In CommonDataProvider.java:
public static final String DATA_PROVIDER_KILL_BITS = "killBitsArguments";

static Stream<Arguments> killBitsArguments() {
    return Stream.of(
            Arguments.of(1, BigInteger.valueOf(1L)),
            Arguments.of(8, BigInteger.valueOf(255L))
    );
}

// In BitHelperTest.java:
@ParameterizedTest
@MethodSource(CommonDataProvider.DATA_PROVIDER_KILL_BITS)
public void getKillBits_bitsGiven_killBitsEqualsExpectation(int bits, BigInteger killBits) {
    // ...
}
```

Verified in `BitHelperTest.java:21,33,65`.

For sources local to the test class (the streambuffer pattern), the
provider method lives on the test class itself:

```java
static Stream<Arguments> writeMethods() {
    return Stream.of(
            Arguments.of(WriteMethod.BYTE_ARRAY),
            Arguments.of(WriteMethod.INT),
            Arguments.of(WriteMethod.BYTE_ARRAY_WITH_PARAMETER));
}
```

Verified in `StreamBufferTest.java:42-47`.

---

## Mocking the Logger

For Maven plugins (`org.apache.maven.plugin.logging.Log`) — plugin only:

```java
@BeforeEach
public void setUp() {
    mockLog = mock(Log.class);
}

@Test
public void indexSourceRoot_missingFile_logsWarning() {
    // arrange
    final SourceFileIndexer indexer = new SourceFileIndexer(mockLog, ...);

    // act
    indexer.indexSourceRoot(sourceRoot);

    // assert
    verify(mockLog, atLeastOnce()).warn(contains("Skipping"));
}
```

For SLF4J-based repos (BAF, jllama, streambuffer), production code
typically uses the static logger idiom:

```java
private static final Logger LOG = LoggerFactory.getLogger(Foo.class);
```

In tests, use **LogCaptor** to verify expected log output without
mocking the static field:

```java
try (LogCaptor captor = LogCaptor.forClass(Foo.class)) {
    // act
    foo.doSomething();

    // assert
    assertThat(captor.getInfoLogs(), hasItem(containsString("started")));
}
```

Verified in BAF (`LogCaptor` 2.12.6 declared at `pom.xml:84,847`; used
in 5 test files) and jllama (`LoggingSmokeTest`).

---

## Production-side conventions referenced by tests

When TDD drives production code, these are the conventions tests assume
and reinforce:

- **Named constants with Javadoc.** Every meaningful string/number/flag
  literal must be a `public static final` or `private static final`
  named constant with a Javadoc comment. Verified in BAF: 141
  `static final` declarations across 29 source files.
- **Custom domain exceptions.** Throw a specific named exception type
  rather than generic `IllegalArgumentException` / `RuntimeException`
  when a domain meaning is involved. BAF examples:
  `KeyProducerIdNullException`, `PrivateKeyTooLargeException`.
- **Constructor injection.** Dependencies arrive through the constructor
  (with `private final` fields) so tests can substitute fakes. Loggers
  are an exception in SLF4J-using repos (static-field `Logger`); inject
  the `Log` when using Maven `Log`.
- **`@VisibleForTesting`** (Guava annotation) marks members that exist
  only to support tests. Used in BAF (16 sites); see
  `policies/code-quality-todos.md` for the design-fit review.

For the Java 21 idioms (records, switch expressions, text blocks,
pattern matching) that apply to BitcoinAddressFinder but not the
Java-8 repos, see
[`../../../guides/src/CODE_WRITING_GUIDE-21.md`](../../../guides/src/CODE_WRITING_GUIDE-21.md).

---

## What NOT To Do

| Anti-pattern | Correct alternative |
|---|---|
| `import org.junit.Test` (JUnit 4) | `import org.junit.jupiter.api.Test` |
| `@RunWith(DataProviderRunner.class)` | `@ParameterizedTest` + `@MethodSource` |
| `@Rule public TemporaryFolder folder = new TemporaryFolder()` | `@TempDir Path folder` |
| `Assert.assertEquals(expected, actual)` | `assertThat(actual, is(equalTo(expected)))` |
| `Assert.assertTrue(condition)` | `assertThat(condition, is(true))` |
| `Assert.assertNotNull(x)` | `assertThat(x, is(notNullValue()))` |
| `Objects.requireNonNull(x)` as guard in tests | `// pre-assert` with `assertThat(x, is(notNullValue()))` |
| `System.out.println(...)` in tests | Remove; use LogCaptor / mock-Log assertions instead |
| Missing `// arrange / act / assert` comments | Add the section comments always |
| Mixing `<editor-fold>` and `@Nested` styles in one file | Pick one and stay consistent |
| `/* license */` block instead of SPDX lines | Use the SPDX single-line form |

---

## Preserving Existing Comments

When modifying existing test code:

- **Keep all existing inline comments** that are correct and descriptive.
- **Only remove a comment** if it is factually wrong, misleading, or
  describes code that no longer exists.
- **Add new comments** where added code is not self-explanatory.
- When adding AAA section comments, place them **around** existing
  inline comments — do not replace them.

The goal is to **minimize the diff** to only lines that actually need
changing.
