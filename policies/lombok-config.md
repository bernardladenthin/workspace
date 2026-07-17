# Lombok Config

> Canonical workspace policy. Sibling repos that use Lombok ship a `lombok.config`
> at the repository root with the content below verbatim. Each sibling repo's
> `CLAUDE.md` points to this file instead of duplicating the rationale.

## Scope

Three sibling repos use Lombok today and therefore carry `lombok.config`:

| Repo | Java target | Lombok use |
|---|---|---|
| `BitcoinAddressFinder` | Java 21 | `@Data` / `@Value` / `@Getter` on configuration POJOs |
| `java-llama.cpp` | Java 8 | `@EqualsAndHashCode` / `@ToString` on value classes |
| `llamacpp-ai-index-maven-plugin` | Java 8 | `@Getter` on Mojo `@Parameter` POJOs |

`streambuffer` does **not** use Lombok (no `lombok.config`, no Lombok
dependency) and is out of scope.

## Why a config file at all

Lombok's defaults are wrong for our SpotBugs + fb-contrib + `-Werror`
pipeline. Without explicit settings, every Lombok-generated value class
surfaces dozens of synthetic-bytecode findings and the build fails on
the very first `@EqualsAndHashCode` annotation. The settings below are
load-bearing — none of them is optional.

## Canonical content

Copy verbatim into `<repo-root>/lombok.config`:

<!-- REUSE-IgnoreStart -->
```
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

# Stop the config-resolution from bubbling up into parent directories.
config.stopBubbling = true

# Emit @lombok.Generated on every generated member. SpotBugs / JaCoCo /
# SonarQube special-case this annotation and skip the synthetic methods
# from coverage requirements and bug detectors. Without this, SpotBugs at
# effort=Max + threshold=Low surfaces dozens of synthetic-bytecode findings
# (USBR_UNNECESSARY_STORE_BEFORE_RETURN, IMC_IMMATURE_CLASS_NO_TOSTRING,
# NM_FIELD_NAMING_CONVENTION, ...) on every Lombok-generated method.
lombok.addLombokGeneratedAnnotation = true

# Default to "skip" on @EqualsAndHashCode / @ToString: we inherit from
# Object in almost all cases; "skip" is the right default for
# Object-extending classes. Classes that extend a non-Object base override
# per-annotation with @EqualsAndHashCode(callSuper = true) /
# @ToString(callSuper = true). Without this, Lombok emits a WARNING on
# every @EqualsAndHashCode without explicit callSuper, which -Werror
# promotes to a build break.
lombok.equalsAndHashCode.callSuper = skip
lombok.toString.callSuper = skip

# Force Lombok's @EqualsAndHashCode / @ToString to read FIELDS directly
# instead of routing through `this.getX()` (the default). Rationale:
#
# Some classes expose value-add getters that wrap their @Nullable field in
# Optional<T> or wrap a list field in Collections.unmodifiableList + Optional.
# Those wrappers are the public-API contract, not the equality contract:
#
#   1. fb-contrib's OI_OPTIONAL_ISSUES_CHECKING_REFERENCE fires on every
#      Lombok-generated `this$x == null` branch when `x` is an Optional —
#      Optional is the standard "never null" type, so the null branch is
#      dead code.
#   2. unmodifiableList + Optional wrapper getters allocate fresh wrappers
#      on every equals call. Field access avoids the allocations.
#   3. The two forms are semantically equivalent: Optional.equals and
#      Collections.unmodifiableList(x).equals(...) both delegate to value-
#      based comparison of the underlying state.
#
# All value classes in these repos are `final`, so subclass-override of a
# getter cannot change equality. callSuper=true chains are unaffected —
# `super.equals()` is still a method call, and the parent class's own
# field handling is governed by the same setting.
lombok.equalsAndHashCode.doNotUseGetters = true
lombok.toString.doNotUseGetters = true

# Do NOT generate Spring-style @ConstructorProperties; java.beans is not
# needed by this codebase and pulls in the desktop module on some JDKs.
lombok.anyConstructor.addConstructorProperties = false

# Allow Lombok-style accessor patterns without warnings.
lombok.accessors.flagUsage = ALLOW
```
<!-- REUSE-IgnoreEnd -->

## Why each setting earns its keep

| Setting | What it does | What happens if removed |
|---|---|---|
| `config.stopBubbling = true` | Stops Lombok config inheritance from parent dirs | Stray configs in `/home/user/` or upstream could leak into the build |
| `lombok.addLombokGeneratedAnnotation = true` | Emits `@lombok.Generated` on every synthetic method | SpotBugs / fb-contrib report 20+ findings on every Lombok class (USBR, IMC_NO_TOSTRING, NM_FIELD_NAMING, ...) |
| `lombok.equalsAndHashCode.callSuper = skip` | No callSuper default → explicit decision per class | Lombok warning on every `@EqualsAndHashCode` → `-Werror` fails the build |
| `lombok.toString.callSuper = skip` | Same for `@ToString` | Same |
| `lombok.equalsAndHashCode.doNotUseGetters = true` | Field-access in generated equals/hashCode | fb-contrib `OI_OPTIONAL_ISSUES_CHECKING_REFERENCE` fires on every Optional-wrapping getter; `Collections.unmodifiableList(...)` + `Optional` allocated on every equals call |
| `lombok.toString.doNotUseGetters = true` | Field-access in generated toString | Same Optional-wrapping noise in rendered toString |
| `lombok.anyConstructor.addConstructorProperties = false` | No `@ConstructorProperties` emitted | Pulls in `java.beans` (desktop module) on some JDKs |
| `lombok.accessors.flagUsage = ALLOW` | No nag on accessor patterns | Lombok warns about accessor-style fields |

## When to deviate per-repo

Two cases warrant a per-class override **inside the affected class** (NOT
in `lombok.config`):

1. **Subclass-override is the equality contract.** A non-`final` class whose
   subclass overrides a getter to change the value participating in equality
   should annotate the parent with `@EqualsAndHashCode(doNotUseGetters = false)`.
   No such class exists in any sibling repo today.

2. **Getter has lazy-init or computed-value semantics that equality must
   see.** Same per-class override. No such class exists today either.

If a third case appears, document it in the affected repo's own `CLAUDE.md`
supplement rather than weakening the workspace policy.

## Sync check

The file lives in each sibling repo's root and the canonical content
above is the source of truth. Manual sync is the only mechanism
today — when the workspace policy changes, update each sibling repo's
`lombok.config` in the same series of commits and bump the corresponding
row in `../crossrepostatus.md`.
