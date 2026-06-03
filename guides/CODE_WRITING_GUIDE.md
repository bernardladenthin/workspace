# Code Writing Guide — Workspace Canonical Conventions

> Canonical workspace guide. Applies to every sibling Java repo
> (`BitcoinAddressFinder`, `java-llama.cpp`, `llamacpp-ai-index-maven-plugin`,
> `streambuffer`). Each repo's own `CODE_WRITING_GUIDE.md` (if present)
> contains only **project-specific supplements**: domain exceptions, repo-
> specific helper classes, framework-specific patterns (e.g. C-prefix
> config POJOs in BAF, Maven `@Parameter` POJOs in the plugin).
>
> For TDD workflow (Red → Green → Refactor, test-first discipline), see
> `.claude/skills/java-tdd-guide/SKILL.md` in this repo.

---

## 1. Named Constants — DRY, No Inline Literals

The primary motivation is **Don't Repeat Yourself (DRY)**. Every meaningful
value must exist in exactly **one** authoritative place — a named constant —
so that a future change requires editing only one line. Inline literals
scatter the same meaning across multiple call sites, making the code
fragile and hard to maintain.

### Rules

- Every string, number, or flag literal that carries semantic meaning
  **must** be a named `public static final` or `private static final`
  constant. Inline magic values are **prohibited**.
- Constants must be placed at the top of the class, before constructors
  and methods.
- The name must describe the **meaning or role** of the value, not the
  value itself.
- Each constant must have a **Javadoc comment** that explains what the
  value represents, why it has that specific value, and any relevant
  cross-references.
- When a derived value (e.g., a string built from a constant prefix) is
  needed, define **both** the source constant and the derived constant,
  and compute the derived one from the source — never duplicate the raw
  literal.

```java
// BAD — magic literals inline, no single source of truth
if (name.endsWith(".ai.md")) { ... }
header.put("h", "1.0");

// GOOD — one authoritative constant with Javadoc
/**
 * File extension appended to every source file name to produce its AI
 * index file name. Example: "MyClass.java" -> "MyClass.java.ai.md".
 */
public static final String AI_MD_EXTENSION = ".ai.md";
```

Repo-specific applications (e.g. BAF's `BitHelper.RADIX_HEX`, the
plugin's header field keys / node-type / provider-name constants) live in
each repo's own supplement.

---

## 2. Logger Injection — Constructor Over Setter

When a class accepts a logger and tests need to inject a mock or stub,
prefer **constructor-based injection** over a setter method.

### Pattern (Maven plugin example using `org.apache.maven.plugin.logging.Log`)

Provide two constructors:

1. **Framework constructor** — the Mojo / framework subclass obtains the
   logger (via `AbstractMojo.getLog()` for Maven plugins) and passes it
   in. This is the constructor used at runtime.
2. **`@VisibleForTesting` constructor** — accepts the logger directly.
   This is the constructor used by tests.

```java
public class SourceFileIndexer {

    private final Log log;

    public SourceFileIndexer(
            final Log log,
            // ... other params
    ) {
        this.log = log;
    }
}
```

Tests pass a `SystemStreamLog`, a mock `Log`, or — for SLF4J-based repos —
a captured `LogCaptor` logger directly.

### Rules

- The `log` field must be `private final`.
- Never expose a `setLog` method on non-framework classes. Constructor
  injection is the only approved mechanism.
- A `setLog` method is the **last resort** — only use it when the object
  is instantiated by a framework that controls construction and
  constructor injection is not feasible.

For repos using SLF4J (BAF, jllama, streambuffer): the same pattern applies
— inject the `org.slf4j.Logger` through the constructor; do not use the
static `LoggerFactory.getLogger(MyClass.class)` field idiom in classes
that have other constructor-injected dependencies, because it defeats
test-time substitution.

---

## 3. Records for Immutable Value Objects

Java `record` types are the preferred representation for immutable data
carriers. Use records when:

- The class holds only final fields that are set at construction.
- There is no mutable state.
- The class has value semantics (equality based on field values).

```java
// GOOD — immutable value object as a record
public record AiSummaryResponse(String text, int tokensGenerated) {}

// BAD — mutable class with getters/setters for a simple data carrier
public class AiSummaryResponse {
    private String text;
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
}
```

**Exception:** Classes instantiated by a framework via reflection (e.g.
Maven's plugin framework reading `@Parameter`-bearing configuration
classes, Jackson deserialising JSON config POJOs) must remain regular
classes with setters or public fields, because the framework cannot
inject values into record components.

---

## 4. Defensive Null and Empty Checks at Public Boundaries

- Validate `null` and empty inputs at the entry point of every public
  method that would otherwise propagate a `NullPointerException` deep
  into a call stack.
- Prefer `log.warn(...)` + early return over silent skips for cases that
  indicate a misconfiguration.
- Throw `IllegalArgumentException` with a descriptive message for
  programming errors (e.g., unsupported target name, missing required
  configuration).

```java
// GOOD — clear error for unsupported configuration
throw new IllegalArgumentException("Unsupported field target: " + target);

// GOOD — warn and skip rather than silently doing nothing
if (!Files.exists(sourceFile)) {
    log.warn("Skipping missing source file: " + sourceFile);
    return false;
}
```

For repos with NullAway enforcement (every sibling repo, in strict
JSpecify mode): the implicit non-null default removes most boundary
checks at compile time, so this rule applies to the input edges that
NullAway cannot prove safe — JSON-deserialised values, file/network
input, reflection-populated fields.

---

## 5. Helper Classes — Instance Methods Over Static Utilities

Helper classes should be designed for mockability and testability, not as
static utility classes.

### Rules

- **Prefer instance methods over static methods.** Helper classes must be
  regular classes (not `final`), with **instance methods** (not `static`).
- **No private constructor.** Do not enforce non-instantiation; allow
  normal object creation.
- **Dependency injection.** Store an instance as a field in classes that
  use the helper, making the dependency explicit and testable.
- **Easy to mock.** Instance methods can be overridden or mocked in tests,
  enabling better test isolation.

### When static methods ARE acceptable

Static methods are acceptable **only** for:

- Pure mathematical functions with no side effects;
- Trivial string/number formatting that never needs to be mocked;
- Constant lookup functions that have no external dependencies.

### Example

```java
// BAD — static utility, not mockable
public final class CompatibilityHelper {
    private CompatibilityHelper() { }
    public static boolean isBlank(final String str) { ... }
}

// GOOD — instance method, mockable
public class CompatibilityHelper {
    public boolean isBlank(final String str) { ... }
}

// In the class that uses it:
public class Factory {
    private final CompatibilityHelper compat = new CompatibilityHelper();
    public Foo create(final String name) {
        if (name == null || compat.isBlank(name)) { ... }
    }
}
```

Migration pattern in BAF: methods originally on `KeyUtility` as `static`
have been moved into `PrivateKeyValidator` as instance methods for the
same reason — see BAF's `CODE_WRITING_GUIDE.md` for the per-method list.

---

## 6. Key-Indexed Definition Pattern

When a configuration block contains a list of named definitions (e.g.
prompt templates, model configs, named producer strategies) that other
parts of the configuration reference by a string key, apply the
**key-indexed definition pattern**:

1. **Definition POJO** — a regular JavaBean class (not a record, because
   the framework injects via reflection) that holds the key and all
   configuration fields. Fields default to the corresponding
   `*Config.DEFAULT_*` constants.
2. **Support class** — converts the list of definition POJOs into a
   `Map<String, ConfigType>` at construction time, then exposes
   `getConfig(String key)` which throws `IllegalArgumentException` (with
   the missing key in the message) for unknown keys.
3. **Reference by key** — any configuration class that previously held an
   inline nested config object is refactored to hold only a
   `String aiDefinitionKey` (or similar) that is resolved at runtime via
   the support class.

### Why this pattern?

- Eliminates duplication when the same parameters are needed in multiple
  places.
- Removes the need for framework profiles (Maven profiles, env-specific
  Spring profiles, etc.) to vary configuration; all definitions live
  inline in the configuration block.
- The support class is constructed once per execution and passed into
  collaborators, making the dependency explicit and testable.

Existing implementations: the plugin's `AiPromptDefinition` /
`AiPromptSupport` and `AiModelDefinition` / `AiModelDefinitionSupport`.
BAF's `KeyProducer`-by-id resolution is the same idea applied to
producer-strategy lookups.

---

## License Headers

Every source file across every sibling repo must include the Apache 2.0
license header wrapped in `// @formatter:off` / `// @formatter:on`. See
any existing source file for the template. The year must match the file
creation year (not the current year).
