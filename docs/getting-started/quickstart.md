# Quick Start

Get your first Hytale plugin running in 5 minutes.

## Prerequisites

- Java 21 or higher
- Maven 3.8+
- A Hytale server JAR

## Step 1: Create Your Project

Create a new directory for your plugin:

```bash
mkdir my-hytale-plugin
cd my-hytale-plugin
```

## Step 2: Create pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-plugin</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.hypixel.hytale</groupId>
            <artifactId>hytale-server</artifactId>
            <version>2026.01.15</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <finalName>${project.artifactId}</finalName>
    </build>
</project>
```

## Step 3: Create Your Plugin Class

Create `src/main/java/com/example/MyPlugin.java`:

```java
package com.example;

import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;

public class MyPlugin extends JavaPlugin {

    public MyPlugin(JavaPluginInit init) {
        super(init);
    }

    @Override
    protected void setup() {
        log("MyPlugin is setting up...");
    }

    @Override
    protected void start() {
        log("MyPlugin started!");
    }

    @Override
    protected void shutdown() {
        log("MyPlugin shutting down...");
    }
}
```

## Step 4: Create manifest.json

Create `src/main/resources/manifest.json`:

```json
{
  "Group": "Example",
  "Name": "MyPlugin",
  "Version": "1.0.0",
  "Main": "com.example.MyPlugin",
  "ServerVersion": "*",
  "IncludesAssetPack": false,
  "DisabledByDefault": false
}
```

## Step 5: Build and Run

Build your plugin:

```bash
mvn clean package
```

Copy the JAR from `target/my-plugin.jar` to your server's `plugins/` folder and start the server!

## Next Steps

- Browse the [API Reference](../api-reference.md) to see what's available
- Read the [First Plugin Guide](../guides/first-plugin.md) for more details
- Check out example plugins on GitHub
