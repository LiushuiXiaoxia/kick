# CLAUDE.md — Kick

Kick is a Kotlin Multiplatform debugging toolkit built on Compose Multiplatform. It provides modular inspection tools (logs, network, SQLite, files, settings, Firebase, layout, overlay, runner) embedded directly in apps across Android, iOS, Desktop (JVM), and Web (WASM).

## Project Structure

```
kick/
├── main-core/          # Base interfaces, common UI, Component/Module abstractions
├── main-runtime/       # Full runtime implementation with inspection UI
├── main-runtime-stub/  # No-op stub for release builds
├── gradle-plugin/      # Gradle plugin (ru.bartwell.kick) for dependency management
├── module/             # Feature modules, each with runtime + stub variants
│   ├── sqlite/         # SQLite inspection (core, runtime, room-adapter, sqldelight-adapter, stubs)
│   ├── logging/        # Log capture and viewer
│   ├── network/        # Ktor3 HTTP traffic inspection
│   ├── settings/       # Multiplatform Settings viewer, Control Panel
│   ├── files/          # File explorer
│   ├── firebase/       # FCM and Analytics inspection (Android/iOS)
│   └── ui/             # Layout inspection utilities
├── maven-publishing/   # Convention plugin for Maven Central publishing
├── sample/             # Sample apps (android, desktop, web, ios, shared, plugin-sample)
├── config/detekt/      # Detekt configuration and baseline
└── content/            # Documentation and wizard web content
```

## Tech Stack & Versions

- Kotlin 2.3.20, KSP 2.3.6
- Compose Multiplatform 1.10.3
- AGP 9.1.0, Gradle 9.3.1
- Decompose 3.3.0 (navigation)
- SQLDelight 2.1.0, Room 2.7.2
- Ktor 3.2.2
- Kotlinx Coroutines 1.10.2, Serialization 1.7.3
- Java 17 (Temurin)

Version catalog: `gradle/libs.versions.toml`

## Build Commands

```bash
# Build
./gradlew assembleDebug                    # Android debug
./gradlew :sample:desktop:run              # Run desktop sample
./gradlew :sample:web:wasmJsBrowserRun     # Run web sample

# Test
./gradlew test                             # All unit tests
./gradlew :gradle-plugin:test              # Gradle plugin tests only

# Code Quality
./gradlew detektCheckAll                   # Run detekt checks
./gradlew detektFixAll                     # Auto-fix detekt issues
./gradlew detektFixThenCheckAll            # Fix then check

# Publishing
./gradlew publishToMavenLocal              # Publish to local Maven
```

## Architecture

- **Module pattern**: Each feature has a runtime implementation and a no-op stub. The Gradle plugin or `isRelease` flag selects which variant to include.
- **Component model**: Decompose-based. `Module` interface provides `getComponent()`, `Content()`, and `registerSubclasses()`. Navigation uses `RootComponent` with a child stack.
- **Initialization**: `Kick.init(context) { module(SomeModule()) }` — singleton pattern via `Kick.Companion.instance`.
- **Gradle plugin** (`ru.bartwell.kick`): DSL `kick { enabledAuto(); modules { ... } }`. Priority: CLI `-Pkick.enabled` > `enableKick()` > DSL block. Auto mode detects release tasks by name.

## Code Style

- Kotlin official style, max line length 120, indent 4 spaces
- Detekt with compose rules, max issues = 0, warnings as errors
- Import order: `*,java.**,javax.**,kotlin.**,^`

## CI/CD

- **build.yml**: Builds all platforms + runs tests (triggered on feature branches and PRs)
- **review.yml**: Plugin tests, lint, detekt, Danger (triggered on PRs to develop)
- **publish.yml**: Publishes to Maven Central + GitHub release (triggered on version tags `v*.*.*`)
- **pages-wizard.yml**: Deploys integration wizard to GitHub Pages

## Key Conventions

- Group ID: `ru.bartwell.kick`
- Library version in `version.properties`, release flag in `settings.properties`
- Targets: Android (minSdk 24, compileSdk 35), iOS (X64/Arm64/SimulatorArm64 static frameworks), JVM, WASM
- Platform-specific source sets: `commonMain`, `androidMain`, `iosMain`, `jvmMain`, `wasmJsMain`, `nativeMain`, `nonWasmMain`
- Main branch: `develop`
