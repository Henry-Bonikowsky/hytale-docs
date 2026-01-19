# API Reference

Complete API documentation for all public classes in the Hytale server plugin API.

## Overview

This reference covers **5,200+ classes** extracted from `hytale-server-2026.01.15.jar`. All documentation is generated directly from the bytecode signatures using `javap`.

## Core Packages

### Plugin System
Core classes for creating and managing plugins.

- [JavaPlugin](classes/JavaPlugin.html) - Base class for all plugins
- [PluginBase](classes/PluginBase.html) - Abstract plugin foundation
- [PluginClassLoader](classes/PluginClassLoader.html) - Plugin class loading
- [PluginType](classes/PluginType.html) - Plugin type enumeration

### Event System
Event registration and handling.

- [EventRegistry](classes/EventRegistry.html) - Event registration manager
- [IEvent](classes/IEvent.html) - Base event interface

### Asset Management
Asset loading and registration.

- [AssetModule](classes/AssetModule.html) - Asset module management
- [AssetPackRegisterEvent](classes/AssetPackRegisterEvent.html) - Asset pack events

### Commands
Command system for plugin commands.

- [CommandOwner](classes/CommandOwner.html) - Command ownership interface

## Browse All Classes

The complete API reference is available in the generated HTML files. Use the search feature (top of page) to find specific classes, methods, or packages.

### Package Structure

- `com.hypixel.hytale.server.*` - Server-side API
- `com.hypixel.hytale.event.*` - Event system
- `com.hypixel.hytale.component.*` - Component system
- `com.hypixel.hytale.assetstore.*` - Asset management
- `com.hypixel.hytale.codec.*` - Serialization
- And many more...

## Using the API Reference

Each class page includes:

- **Class signature** - Full declaration with modifiers
- **Description** - What the class does
- **Fields** - Public and private fields (toggle visibility)
- **Constructors** - How to instantiate the class
- **Methods** - Available methods and their signatures

## Notes

- All type references are clickable - click to navigate to that class
- Use the visibility toggle to show/hide private members
- Generated descriptions are factual extractions from signatures
- For detailed implementation info, consult the server JAR

## Version

This documentation is for **Hytale Server 2026.01.15**.

---

**Not affiliated with Hypixel Studios**
