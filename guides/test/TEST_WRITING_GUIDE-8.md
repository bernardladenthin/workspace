# Test Writing Guide — Test Sources — Java 8 (baseline)

> **Versioned guide chain.** Files in this directory follow the naming
> convention `TEST_WRITING_GUIDE-<JAVA-VERSION>.md`. A higher-version
> file inherits all rules from every lower-version file in the chain
> and may add new rules or override individual rules from below.
> Read every file from the lowest applicable version up to the highest
> one your repo's `pom.xml` `<release>` allows.
>
> | File | Applies to | Inherits from |
> |---|---|---|
> | [`TEST_WRITING_GUIDE-8.md`](TEST_WRITING_GUIDE-8.md) (this file) | every sibling Java repo | — (baseline) |
> | [`TEST_WRITING_GUIDE-21.md`](TEST_WRITING_GUIDE-21.md) | `BitcoinAddressFinder` only (Java 21) | `-8.md` |
>
> When a repo upgrades to a new LTS, add a new
> `TEST_WRITING_GUIDE-<NEW>.md` file rather than editing older ones.
>
> **This file (Java 8 baseline):** applies to every sibling Java repo.
> Reflects the conventions **actually in use** across the codebases —
> verified by reading test sources, not invented. The owner's
> ground-truth references are
> [`BitcoinAddressFinder`](https://github.com/bernardladenthin/BitcoinAddressFinder)
> and
> [`streambuffer`](https://github.com/bernardladenthin/streambuffer),
> which are hand-written. The other two repos are predominantly
> AI-generated and have weaker style fidelity.
>
> For the TDD workflow and the larger framework rationale, see
> [`../../.claude/skills/java-tdd-guide/SKILL.md`](../../.claude/skills/java-tdd-guide/SKILL.md).

---

## 1. File header — SPDX

Every test file **must** start with the SPDX-format license header:

<!-- REUSE-IgnoreStart -->
```java
// SPDX-FileCopyrightText: <YEAR-RANGE> Bernard Ladenthin <bernard.ladenthin@gmail.com>
//
// SPDX-License-Identifier: Apache-2.0
package net.ladenthin.<repo>;
```

- Three single-line `//` comments.
- No `// @formatter:off` / `// @formatter:on` wrapper.
- `<YEAR-RANGE>` is the file's actual lifespan (e.g. `2017-2026`).
- jllama uses `SPDX-License-Identifier: MIT` with a dual-copyright
  line (Konstantin Herud upstream attribution); everywhere else is
  `Apache-2.0`.

<!-- REUSE-IgnoreEnd -->

REUSE-tool compliance is enforced in CI in every repo.

---

## 2. Test Framework — the actually-used stack

| Concern | Choice |
|---|---|
| Runner | JUnit Jupiter 6.1.0 (`org.junit.jupiter.api.*`) |
| Assertions | Hamcrest 3.0 (`assertThat(actual, is(equalTo(expected)))`) |
| Parameterized | `@ParameterizedTest` + `@MethodSource(SourceClass.CONSTANT_NAME)` |
| Mocking | Mockito (BAF, plugin) |
| Temp filesystem | `@TempDir Path folder` |
| SLF4J log capture | `LogCaptor` (BAF, jllama) |

**Do NOT use:**

- `org.junit.*` (JUnit 4) — banned via Maven Enforcer in every repo.
- `@RunWith(DataProviderRunner.class)` — not used in any repo.
- TestNG.
- `Assertions.assertEquals` / `assertTrue` / `assertFalse` /
  `assertNotNull` from `org.junit.jupiter.api.Assertions` when Hamcrest
  can express it more clearly.

**Two narrow Jupiter-assertion exceptions** that ARE used in practice:

- `assertThrows` / `assertDoesNotThrow` — Hamcrest has no equivalent.
- `assertArrayEquals(byte[], byte[])` — used in streambuffer for
  byte-array equality where Hamcrest's `is(equalTo(...))` would compare
  references instead of content.

---

## 3. Class-Level Setup

### Class Declaration

```java
public class FooTest {
```

No runner annotation. Class-level `@Timeout(value = 20, unit = TimeUnit.SECONDS)`
is appropriate for tests that may hang on bugs (verified in
`StreamBufferTest.java:39`).

### Shared Instance Fields

Declare shared utilities as `private final` instance fields:

```java
private final BitHelper bitHelper = new BitHelper();
```

Mocks that need fresh state per test are declared at field level but
initialized in `@BeforeEach`:

```java
private Log mockLog;

@BeforeEach
public void setUp() {
    mockLog = mock(Log.class);
}
```

Omit an empty `@BeforeEach` method entirely.

### TempDir

Prefer `Files.createTempDirectory(...)` for one-off temp directories
within a single test. Use `@TempDir` when multiple tests in the same
class share the same temporary root:

```java
@TempDir
public Path folder;
```

---

## 4. Two equally valid grouping styles

The owner's codebases use two different patterns to group related
tests within a class. **Both are accepted**; pick the style that
matches the surrounding file and stay consistent.

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

Rules:

- `desc` equals the method name (or a short feature label).
- `defaultstate="collapsed"` is mandatory.
- One fold per method/feature under test.
- Tests for different methods MUST be in different folds.

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

Rules:

- Each `@Nested` class groups tests for a related behaviour.
- `@DisplayName` provides the human-readable label.
- `@Nested` classes are non-static inner classes.

**Do not mix styles in one file.** If you're editing a `<editor-fold>`-
style file, keep adding folds; if you're editing a `@Nested`-style
file, keep adding `@Nested` classes.

---

## 5. Test Method Naming

Default pattern: **`methodUnderTest_inputOrCondition_expectedBehavior`**

```
getKillBits_bitsGiven_killBitsEqualsExpectation
convertBitsToSize_bitsGiven_sizeEqualsExpectation
assertBatchSizeInBitsIsInRange_bitsGivenBelowMinimum_exceptionThrown
indexSourceRoot_emptyDirectory_returnsZero
```

Rules for the default pattern:

- All three segments are required and separated by underscores.
- camelCase within each segment.
- The `expected` segment describes the observable outcome
  (`_returnsZero`, `_throwsException`, `_exceptionThrown`,
  `_skipsFile`, `_roundtripsCorrectly`).
- Exception tests end with `_throwsException` or `_exceptionThrown`.
- No-op / smoke tests use `_noExceptionThrown`.

**Inside `@Nested` classes (Style B)**, naming MAY relax to
`testFoo` / `testSimpleRoundTrip` because `@DisplayName` carries the
readable label. Do not relax naming in non-`@Nested` classes.

---

## 6. Test Body — AAA Structure

Every test body **must** follow the Arrange / Act / Assert structure
with explicit section comments. Verified usage: BAF 323+ matches across
10 files; sb 658 matches in one file; plugin 129 across 10 files.

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

The combined `// act, assert` form is acceptable when the act IS the
assertion (verified in `BitHelperTest.java:26,38,49`):

```java
@Test
public void getKillBits_bitsGiven_killBitsEqualsExpectation(int bits, BigInteger killBits) {
    // arrange
    BitHelper bitHelper = new BitHelper();

    // act, assert
    assertThat(bitHelper.getKillBits(bits), is(equalTo(killBits)));
}
```

### `// pre-assert` — two valid positions

**1. Before `// act`** — to verify a precondition of the input:

```java
// arrange
final AiMdDocument document = documentCodec.read(aiFile);

// pre-assert
assertThat(document.header().s(), is(emptyOrNullString()));

// act
final int count = indexer.indexSourceRoot(sourceRoot);

// assert
assertThat(count, is(equalTo(1)));
```

**2. Between `// act` and `// assert`** — as a null-guard before
accessing fields:

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
- Keep the act to a single method call whenever possible.
- Do **not** use `Objects.requireNonNull(...)` as a guard in tests; use
  `// pre-assert` with `assertThat(x, is(notNullValue()))`.

---

## 7. Assertions — Hamcrest Style

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

**Imports:**

```java
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
// or specific:
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
```

Allowed Jupiter assertions alongside Hamcrest:

```java
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;  // byte-array compare
```

---

## 8. Exception Testing

```java
// Simple expected exception
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

---

## 9. Parameterized Tests — `@MethodSource`

Owner's pattern: store method-source names as named string constants
on a `CommonDataProvider` (or sibling provider) class, then reference
them symbolically from `@MethodSource`. Prevents typos and makes
provider methods easy to locate.

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

For sources local to the test class (streambuffer pattern), the
provider method lives directly on the test class:

```java
static Stream<Arguments> writeMethods() {
    return Stream.of(
            Arguments.of(WriteMethod.BYTE_ARRAY),
            Arguments.of(WriteMethod.INT),
            Arguments.of(WriteMethod.BYTE_ARRAY_WITH_PARAMETER));
}
```

---

## 10. Mocking the Logger

For SLF4J-based repos (BAF, jllama, streambuffer), production code
uses the static-field idiom
(`private static final Logger LOG = LoggerFactory.getLogger(Foo.class)`).
In tests, use **LogCaptor**:

```java
try (LogCaptor captor = LogCaptor.forClass(Foo.class)) {
    // act
    foo.doSomething();

    // assert
    assertThat(captor.getInfoLogs(), hasItem(containsString("started")));
}
```

Verified in BAF (`LogCaptor` 2.12.6 in 5 test files) and jllama
(`LoggingSmokeTest`).

For Maven plugins (plugin only), the `Log` is constructor-injected and
can be mocked with Mockito:

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

---

## 11. Import Style

Group imports in this order (no blank lines within groups, blank line
between groups):

1. Standard Java (`java.*`, `javax.*`)
2. Third-party libraries (alphabetical)
3. Project classes (`net.ladenthin.*`)
4. Static imports (last, alphabetical)

Prefer specific static imports over wildcards when only one or two
matchers are used:

```java
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
```

Use wildcard static import when many matchers are used:

```java
import static org.hamcrest.Matchers.*;
```

---

## 12. Constants — DRY Within a Fold / `@Nested` Class

When the same literal appears in two or more tests within the same
grouping, extract it to a `private static final` constant.

```java
// GOOD — one definition; both tests derive from it
private static final String FIXED_CHECKSUM = "AAAAAAAA";
```

Constants belong to their logical group. Do not share a constant
between unrelated groups even when the underlying value is identical.

---

## 13. What NOT To Do

| Anti-pattern | Correct alternative |
|---|---|
| `import org.junit.Test` (JUnit 4) | `import org.junit.jupiter.api.Test` |
| `@RunWith(DataProviderRunner.class)` | `@ParameterizedTest` + `@MethodSource` |
| `@Rule public TemporaryFolder folder = new TemporaryFolder()` | `@TempDir Path folder` |
| `Assert.assertEquals(expected, actual)` | `assertThat(actual, is(equalTo(expected)))` |
| `Assert.assertTrue(condition)` | `assertThat(condition, is(true))` |
| `Assert.assertNotNull(x)` | `assertThat(x, is(notNullValue()))` |
| `Objects.requireNonNull(x)` as guard in tests | `// pre-assert` with `assertThat(x, is(notNullValue()))` |
| `System.out.println(...)` in tests | Remove; use LogCaptor / mock-Log instead |
| Missing `// arrange / act / assert` comments | Add the section comments always |
| Mixing `<editor-fold>` and `@Nested` styles in one file | Pick one and stay consistent |
| `/* license */` block | Use the SPDX single-line form |
| `// @formatter:off` wrapper around the license | Remove — not needed for SPDX |
| Non-conforming test name like `shouldDoFoo()` | Rename to `doFoo_condition_expectation()` |
| Empty `@BeforeEach` method | Remove it |
| Hard-coded paths like `"/tmp/test"` | Use `Files.createTempDirectory(...)` or `@TempDir` |

---

## 14. Preserving Existing Comments

When modifying existing test code:

- Keep all existing inline comments that are correct and descriptive.
- Only remove a comment if it is factually wrong, misleading, or
  describes code that no longer exists.
- Add new comments where added code is not self-explanatory.
- When adding AAA section comments, place them **around** existing
  inline comments — do not replace them.

The goal is to **minimize the diff** to only lines that actually need
changing.

---

## 15. Repo-specific supplements

| Repo | Project-specific test conventions |
|---|---|
| BAF | Custom marker annotations (`@AwaitTimeTest`, `@OpenCLTest`, `@ToStringTest`); `OpenCLPlatformAssume` / `LMDBPlatformAssume`; `StaticKey` / `TestAddresses42` / `P2PKH` enum constants; `LMDBBase` / `AbstractProducerTest` shared base classes; socket test helpers via `TestTimeProvider` / `ConnectionUtils`; `CommonDataProvider.DATA_PROVIDER_*` parameter constants. Style: `<editor-fold>`, strict naming. |
| streambuffer | jcstress + Lincheck + vmlens opt-in concurrency profiles; JMH benchmarks via `exec-maven-plugin`; class-level `@Timeout(20s)`. Style: `@Nested` + `@DisplayName`, relaxed naming inside `@Nested`. |
| jllama | C++ GoogleTest pattern (`test_json_helpers.cpp`, `test_jni_helpers.cpp`); JNI mock via zero-filled `JNINativeInterface_`; multimodal integration test self-skip via system properties. AI-generated; use BAF/sb for Java style reference. |
| plugin | LLM integration tests with `LlamaCppJniAvailability.isAvailable()` guard + bundled `SmolLM2-135M-Instruct-Q3_K_M.gguf` model; Maven `Log` mocked via Mockito. AI-generated; use BAF/sb for Java style reference. |

These supplements compose with — not replace — the canonical rules
above.
