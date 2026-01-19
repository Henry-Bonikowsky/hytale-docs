# Installation

Learn how to set up your development environment for Hytale plugin development.

## Requirements

- **Java 21** or higher ([Download](https://adoptium.net/))
- **Maven 3.8+** ([Download](https://maven.apache.org/download.cgi))
- **Hytale Server JAR** (version 2026.01.15 or compatible)
- **IDE** (IntelliJ IDEA recommended, VSCode works too)

## Installing Java 21

### Windows

1. Download Java 21 from [Adoptium](https://adoptium.net/)
2. Run the installer
3. Verify: `java -version`

### macOS

```bash
brew install openjdk@21
```

### Linux

```bash
sudo apt install openjdk-21-jdk  # Ubuntu/Debian
sudo dnf install java-21-openjdk # Fedora
```

## Installing Maven

### Windows

1. Download from [Maven website](https://maven.apache.org/download.cgi)
2. Extract to `C:\Program Files\Maven`
3. Add to PATH: `C:\Program Files\Maven\bin`
4. Verify: `mvn -version`

### macOS

```bash
brew install maven
```

### Linux

```bash
sudo apt install maven  # Ubuntu/Debian
sudo dnf install maven  # Fedora
```

## IDE Setup

### IntelliJ IDEA (Recommended)

1. Download [IntelliJ IDEA](https://www.jetbrains.com/idea/download/) (Community Edition is free)
2. Install the Maven plugin (usually pre-installed)
3. Create new Maven project
4. Set SDK to Java 21

### VS Code

1. Install [VS Code](https://code.visualstudio.com/)
2. Install extensions:
   - Extension Pack for Java
   - Maven for Java
3. Open your plugin folder

## Getting the Hytale Server JAR

The Hytale server JAR should be installed in your local Maven repository. If you have the server installed, it's typically at:

```
~/.m2/repository/com/hypixel/hytale/hytale-server/2026.01.15/
```

If you need to install it manually:

```bash
mvn install:install-file \
  -Dfile=path/to/hytale-server-2026.01.15.jar \
  -DgroupId=com.hypixel.hytale \
  -DartifactId=hytale-server \
  -Dversion=2026.01.15 \
  -Dpackaging=jar
```

## Verify Installation

Create a test project to verify everything works:

```bash
mvn archetype:generate -DgroupId=com.test -DartifactId=test-plugin
cd test-plugin
mvn clean package
```

If this succeeds, you're ready to start developing!

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to create your first plugin
- Browse the [API Reference](../api-reference.md)
