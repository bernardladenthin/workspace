# Test Writing Guide — Workspace Canonical Conventions

> Canonical workspace guide. Applies to every sibling Java repo
> (`BitcoinAddressFinder`, `java-llama.cpp`, `llamacpp-ai-index-maven-plugin`,
> `streambuffer`). Each repo's own `TEST_WRITING_GUIDE.md` (if present)
> contains only **project-specific supplements**: custom marker annotations,
> platform-assume helpers, LMDB / OpenCL / JNI integration patterns.
>
> For the underlying TDD workflow (Red → Green → Refactor), see
> `.claude/skills/java-tdd-guide/SKILL.md` in this repo.
>
> **Heads-up on framework drift.** The skill specifies JUnit 4, but BAF
> (`junit-jupiter` 6.0.3) and the plugin (`junit-jupiter` 6.1.0) actually
> run JUnit Jupiter. This guide documents the JUnit Jupiter conventions
> the active repos use; the skill text needs a reconciliation pass that
> hasn't happened yet.

---

## 1. File Structure & Header

Every test file **must** start with the formatter-off block enclosing the
Apache 2.0 license header:

```java
// @formatter:off
/**
 * Copyright <YEAR> Bernard Ladenthin <email>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
// @formatter:on
package net.ladenthin.<repo>;
```

- The `// @formatter:off` / `// @formatter:on` pair wraps **only** the
  license block.
- The year must match the file creation year (not the current year).

---

## 2. Test Framework

| Concern | Choice |
|---|---|
| Test runner | JUnit Jupiter (`@Test`, `@BeforeEach`, `@TempDir`) from `org.junit.jupiter.api.*` |
| Parameterized tests | `@ParameterizedTest` + `@MethodSource` / `@ValueSource` / `@CsvSource` |
| Assertions | Hamcrest only — `assertThat(actual, is(equalTo(expected)))` |
| Mocking | Mockito (`mock()`, `verify()`, `when()`, `ArgumentCaptor`) |
| Temp file system | `Files.createTempDirectory(...)` or `@TempDir Path folder` |
| SLF4J log capture (where applicable) | `LogCaptor` |

**Do NOT use:**

- `Assertions.assertEquals` / `Assertions.assertTrue` / `Assertions.assertFalse`
  — use Hamcrest equivalents.
- TestNG, JUnit 4, or JUnit 5 vintage runner.

---

## 3. Class-Level Setup

### Class Declaration

```java
public class FooTest {
```

No runner annotation is required — JUnit Jupiter discovers `@Test` and
`@ParameterizedTest` methods automatically.

### Shared Instance Fields

Declare shared utilities as `private final` instance fields:

```java
private final AiMdDocumentCodec documentCodec = new AiMdDocumentCodec();
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

An empty `@BeforeEach` method should be omitted entirely.

### TempDir

Prefer `Files.createTempDirectory(...)` for one-off temp directories
within a single test. Use `@TempDir` when multiple tests in the same
class share the same temporary root:

```java
@TempDir
public Path folder;
```

---

## 4. Code Folding — Grouping Tests by Method Under Test

Tests within a class **must** be grouped using NetBeans-style editor fold
regions, one fold per method/feature under test:

```java
// <editor-fold defaultstate="collapsed" desc="methodName">
@Test
public void methodName_conditionA_expectedResultA() { ... }

@Test
public void methodName_conditionB_expectedResultB() { ... }
// </editor-fold>
```

Rules:

- The `desc` attribute equals the method name (or a short feature label
  for non-method groups).
- `defaultstate="collapsed"` is mandatory on every fold.
- All tests for the same method go inside a single fold.
- Tests that exercise different methods **must** be in different folds.
- The fold order in the file should match logical reading order (simple
  cases first, edge cases and exceptions last).

---

## 5. Test Method Naming

Pattern: **`methodUnderTest_inputOrCondition_expectedBehavior`**

```
indexSourceRoot_emptyDirectory_returnsZero
indexSourceRoot_existingSummaryForceIsFalse_skipsFile
read_validDocument_parsesHeaderAndBody
preparePrompt_sourceLongerThanMax_trimmedFlagIsTrue
```

Rules:

- All three segments are **required** and separated by underscores.
- Use camelCase within each segment.
- The `expected` segment describes the observable outcome, not the
  implementation step.
  - Good: `_returnsZero`, `_throwsException`, `_skipsFile`,
    `_roundtripsCorrectly`
  - Bad: `_works`, `_correct`, `_test`
- Exception tests: the segment ends with `_throwsException` or
  `_exceptionThrown`.
- No-op / smoke tests: use `_noExceptionThrown`.

---

## 6. Test Body — AAA Structure

Every test body **must** follow the Arrange / Act / Assert structure with
explicit section comments:

```java
@Test
public void indexSourceRoot_emptyDirectory_returnsZero() throws Exception {
    // arrange
    final Path temp = Files.createTempDirectory("ai-test");
    final SourceFileIndexer indexer = new SourceFileIndexer(...);

    // act
    final int result = indexer.indexSourceRoot(temp);

    // assert
    assertThat(result, is(equalTo(0)));
}
```

### `// pre-assert` — two valid positions

`// pre-assert` is a named section that asserts a condition without it
being the primary assertion of the test.

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

**2. Between `// act` and `// assert`** — as a guard before accessing
fields:

```java
// act
final AiMdDocument updated = documentCodec.read(aiFile);

// pre-assert
assertThat(updated, is(notNullValue()));

// assert
assertThat(updated.header().s(), is(equalTo("Mock summary for Test.java")));
```

Rules:

- `// arrange` may be omitted only when there is genuinely nothing to
  arrange.
- Keep the act to a **single method call** whenever possible.
- Do **not** use `Objects.requireNonNull(...)` as a guard in tests; use a
  `// pre-assert` with `assertThat(x, is(notNullValue()))`.

---

## 7. Assertions — Hamcrest Style

All assertions use the Hamcrest `assertThat` form:

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
```

Do **not** use:

- `org.junit.Assert.assertEquals`
- `org.junit.Assert.assertTrue` / `assertFalse`
- `Assert.assertNotNull`

---

## 8. Exception Testing

```java
// Simple expected exception
@Test
public void preparePrompt_unsupportedTarget_throwsException() {
    // act / assert
    assertThrows(IllegalArgumentException.class, () -> summarizer.someMethod(null));
}

// Exception with message verification
@Test
public void create_unknownProvider_throwsWithMessage() {
    // arrange
    final AiGenerationProviderFactory factory = new AiGenerationProviderFactory();

    // act
    final IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
            () -> factory.create("unknown-provider", config, promptSupport));

    // assert
    assertThat(e.getMessage(), containsString("unknown-provider"));
}
```

---

## 9. Parameterized Tests

```java
// 1. Constant for the source method name
public static final String SOURCE_NODE_TYPES = "nodeTypes";

// 2. Javadoc linking to which test it serves
/**
 * For {@link AiMdHeaderCodecTest}.
 */
static Stream<String> nodeTypes() {
    return Stream.of(
            AiMdHeaderCodec.NODE_TYPE_FILE,
            AiMdHeaderCodec.NODE_TYPE_PACKAGE
    );
}

@ParameterizedTest
@MethodSource("nodeTypes")
public void roundtrip_validNodeType_preservesValue(final String nodeType) {
    // arrange / act / assert
}
```

For sources shared across multiple test classes, reference a fully-
qualified method:
`@MethodSource("net.ladenthin.<pkg>.CommonDataProvider#nodeTypes")`.

---

## 10. Mocking the Logger

Inject a mock logger to verify that a class logs expected messages.

For Maven plugins (`org.apache.maven.plugin.logging.Log`):

```java
@BeforeEach
public void setUp() {
    mockLog = mock(Log.class);
}

@Test
public void indexSourceRoot_missingSourceFile_logsWarning() {
    // arrange
    final SourceFileIndexer indexer = new SourceFileIndexer(mockLog, ...);

    // act
    indexer.indexSourceRoot(sourceRoot);

    // assert
    verify(mockLog, atLeastOnce()).warn(contains("Skipping missing subtree"));
}
```

For SLF4J-based repos, prefer `LogCaptor`:

```java
try (LogCaptor logCaptor = LogCaptor.forClass(OSInfo.class)) {
    // act
    OSInfo.getHardwareName();

    // assert
    assertThat(logCaptor.getInfoLogs(), hasItem(containsString("arch=")));
}
```

Use `ArgumentCaptor<String>` when the full message content must be
asserted with the mock approach.

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

## 12. Constants — DRY Within a Fold

When the same literal appears in two or more tests within the same fold,
extract it into a `private static final` constant at the class level.

```java
// GOOD — one definition; both tests derive from it
private static final String FIXED_CHECKSUM = "AAAAAAAA";
```

Constants belong to their logical fold. Do not share a constant between
different folds even when the underlying value is identical — different
folds test independent methods and should not be coupled.

---

## 13. What NOT To Do

| Anti-pattern | Correct alternative |
|---|---|
| `Assert.assertEquals(expected, actual)` | `assertThat(actual, is(equalTo(expected)))` |
| `Assert.assertTrue(condition)` | `assertThat(condition, is(true))` |
| `Assert.assertNotNull(x)` | `assertThat(x, is(notNullValue()))` |
| `Objects.requireNonNull(x)` as guard in tests | `// pre-assert` with `assertThat(x, is(notNullValue()))` |
| `System.out.println(...)` in tests | Remove; use logger assertions instead |
| Missing `// arrange / act / assert` comments | Add the section comments always |
| Missing editor fold | Wrap each method group in `<editor-fold>` |
| Non-conforming test name like `shouldSummarizeFile()` | Rename to `summarizeFiles_condition_expectation()` |
| Empty `@BeforeEach` method | Remove it |
| Hard-coded path strings like `"/tmp/test"` | Use `Files.createTempDirectory(...)` |
| Removing existing correct inline comments during a fix | Preserve all correct comments; only remove factually wrong ones |

---

## 14. Preserving Existing Comments

When modifying existing test code:

- **Keep all existing inline comments** that are correct and descriptive.
- **Only remove a comment** if it is factually wrong, misleading, or
  describes code that no longer exists.
- **Add new comments** where added code is not self-explanatory.
- When adding AAA section comments, place them **around** existing inline
  comments — do not replace them.

The goal is to **minimize the diff** to only lines that actually need
changing.

---

## 15. Repo-specific supplements

The following patterns are documented in each repo's own
`TEST_WRITING_GUIDE.md` (when present):

| Repo | Project-specific test conventions |
|---|---|
| BAF | Custom marker annotations (`@AwaitTimeTest`, `@OpenCLTest`, `@ToStringTest`); `OpenCLPlatformAssume` / `LMDBPlatformAssume`; `StaticKey` / `TestAddresses42` / `P2PKH` enum constants; `LMDBBase` / `AbstractProducerTest` shared base classes; socket test helpers via `TestTimeProvider` / `ConnectionUtils` |
| plugin | LLM integration tests with `LlamaCppJniAvailability.isAvailable()` guard + bundled `SmolLM2-135M-Instruct-Q3_K_M.gguf` model |
| jllama | C++ GoogleTest pattern (`test_json_helpers.cpp`, `test_jni_helpers.cpp`); JNI mock via zero-filled `JNINativeInterface_`; multimodal integration test self-skip via system properties |
| streambuffer | jcstress + Lincheck + vmlens opt-in concurrency profiles; JMH benchmarks via `exec-maven-plugin` |

These supplements compose with — not replace — the canonical rules above.
