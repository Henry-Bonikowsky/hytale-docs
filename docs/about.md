# About

## What is this?

Hytale Plugin API Documentation is a comprehensive, searchable reference for all public classes and interfaces available in the Hytale server plugin API.

## How was this created?

This documentation was generated using `javap` to extract method signatures, field definitions, and class hierarchies directly from the Hytale server JAR file (`hytale-server-2026.01.15.jar`).

**No decompilation** - Only public API signatures are extracted, preserving:
- Accurate method signatures
- Proper generic types
- Clean parameter names

## Why does this exist?

The Hytale server JAR contains thousands of classes, but navigating them without documentation is challenging. This project aims to make plugin development more accessible by providing:

- **Searchable documentation** for all public APIs
- **Clickable type references** for easy navigation
- **Dark theme** optimized for readability
- **Organized package structure** for browsing

## Disclaimer

**This project is NOT officially affiliated with Hypixel Studios or the Hytale team.**

This is an independent community project to help plugin developers. All information is extracted from publicly available server JAR files.

## Contributing

Found an issue? Want to improve the documentation?

- Report bugs: [GitHub Issues](https://github.com/Henry-Bonikowsky/hytale-docs/issues)
- Suggest improvements: [GitHub Discussions](https://github.com/Henry-Bonikowsky/hytale-docs/discussions)
- Submit PRs: [GitHub](https://github.com/Henry-Bonikowsky/hytale-docs)

## Technical Details

**Generator**: Python script using `javap` and `jinja2`
**Theme**: Material for MkDocs (dark mode)
**Hosting**: ReadTheDocs + GitHub Pages
**Version**: 2026.01.15
**Classes documented**: 5,200+

## Credits

Created by [Henry Bonikowsky](https://github.com/Henry-Bonikowsky)

Built with:
- Python
- MkDocs
- Material for MkDocs
- ReadTheDocs
- Claude Code (AI assistant)

## License

Documentation content: CC BY 4.0
Generated code/scripts: MIT License

---

**Not affiliated with Hypixel Studios**
