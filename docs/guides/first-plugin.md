# Creating Your First Plugin

A complete walkthrough for building a functional Hytale plugin from scratch.

## What We'll Build

A simple plugin that:
- Logs when it starts
- Registers an event listener
- Responds to player events

## Step 1: Project Setup

Follow the [Quick Start](../getting-started/quickstart.md) to create the basic project structure.

## Step 2: Understanding the Plugin Lifecycle

Every plugin extends `JavaPlugin` and goes through these phases:

```java
public class MyPlugin extends JavaPlugin {

    public MyPlugin(JavaPluginInit init) {
        super(init);
        // Called when plugin is loaded
    }

    @Override
    protected void setup() {
        // Called during setup phase
        // Register events, commands, etc. here
    }

    @Override
    protected void start() {
        // Called when plugin is fully loaded
    }

    @Override
    protected void shutdown() {
        // Called when server is stopping
    }
}
```

## Step 3: Logging

Use the `log()` method provided by `JavaPlugin`:

```java
@Override
protected void start() {
    log("Plugin started successfully!");
}
```

## Step 4: Working with Events

To listen for events, you need to:

1. Get the event registry
2. Register your listener
3. Handle the event

Example:

```java
@Override
protected void setup() {
    // Register event listeners here
    getEventRegistry().register(this);
}
```

## Step 5: Accessing the Plugin Info

Your plugin has access to metadata:

```java
@Override
protected void start() {
    log("Plugin: " + getIdentifier().getName());
    log("Version: " + getManifest().getVersion());
}
```

## Step 6: Building and Testing

Build your plugin:

```bash
mvn clean package
```

Copy to server:

```bash
cp target/my-plugin.jar /path/to/server/plugins/
```

Start the server and check the logs for your messages!

## Common Patterns

### Configuration Files

Store config in your plugin's data folder:

```java
Path configPath = getDataFolder().resolve("config.json");
```

### Dependency Injection

The `JavaPluginInit` provides access to server services during construction.

### Error Handling

Always wrap risky operations:

```java
try {
    // Your code
} catch (Exception e) {
    log("Error: " + e.getMessage());
}
```

## Next Steps

- Browse the [API Reference](../api-reference.md) for available classes
- Look at example plugins on GitHub
- Join the community for help

## Troubleshooting

**Plugin not loading?**
- Check manifest.json has correct Main class
- Verify Java version is 21+
- Look for errors in server logs

**ClassNotFoundException?**
- Ensure dependency is in pom.xml
- Check scope is `provided` for server classes
