# Hytale Plugin API Documentation

Complete, searchable API reference for Hytale server plugins.

🌐 **Live Site**: [hytale-docs.dev](https://hytale-docs.dev)

## What's Inside

- **5,200+ classes** documented from `hytale-server-2026.01.15.jar`
- Full method signatures and field definitions
- Clickable type references for easy navigation
- Dark theme optimized for readability
- Searchable via ReadTheDocs

## Quick Links

- [Getting Started](https://hytale-docs.dev/getting-started/quickstart/)
- [API Reference](https://hytale-docs.dev/api-reference/)
- [Guides](https://hytale-docs.dev/guides/first-plugin/)

## Local Development

Build the docs locally:

```bash
pip install -r requirements.txt
mkdocs serve
```

Visit `http://localhost:8000`

## How It Works

Documentation is generated using:

1. **`javap`** - Extracts public API signatures from the Hytale server JAR
2. **Python script** - Parses signatures and generates HTML
3. **MkDocs** - Builds the site with Material theme
4. **ReadTheDocs** - Hosts with automatic builds

No decompilation - only public API signatures are extracted.

## Structure

```
├── docs/                    # Documentation content
│   ├── index.md            # Landing page
│   ├── getting-started/    # Getting started guides
│   ├── guides/             # Tutorials
│   ├── api-reference.md    # API overview
│   └── classes/            # Generated API docs (5,218 HTML files)
├── assets/                  # CSS and JS for generated docs
├── mkdocs.yml              # MkDocs configuration
├── .readthedocs.yml        # ReadTheDocs build config
├── requirements.txt        # Python dependencies
└── generate-all-docs.py    # Documentation generator script
```

## Contributing

Found an issue? Want to improve the docs?

- [Report bugs](https://github.com/Henry-Bonikowsky/hytale-docs/issues)
- [Suggest improvements](https://github.com/Henry-Bonikowsky/hytale-docs/discussions)
- Submit pull requests

## Disclaimer

**Not affiliated with Hypixel Studios or the Hytale team.**

This is an independent community project to help plugin developers.

## License

- Documentation content: CC BY 4.0
- Generated code/scripts: MIT License

---

Built by [Henry Bonikowsky](https://github.com/Henry-Bonikowsky) with Claude Code
