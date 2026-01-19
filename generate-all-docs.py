#!/usr/bin/env python3
"""
Complete automated documentation generator for Hytale Plugin API.

This script:
1. Extracts javap output for specified classes
2. Generates AI descriptions using Ollama
3. Creates HTML documentation pages
4. Makes all class references clickable

Usage:
    python generate-all-docs.py [class1] [class2] ...

If no classes specified, processes all classes in JAR.
"""

import json
import re
import sys
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
JAR_PATH = Path("C:/Users/henry/.m2/repository/com/hypixel/hytale/hytale-server/2026.01.15/hytale-server-2026.01.15.jar")
OUTPUT_DIR = Path(__file__).parent / "classes"
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_javap(class_name: str) -> Optional[str]:
    """Extract javap output for a class."""
    try:
        result = subprocess.run(
            ["javap", "-private", "-v", "-classpath", str(JAR_PATH), class_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"  Warning: javap failed for {class_name}: {result.stderr}")
            return None
    except Exception as e:
        print(f"  Warning: Error running javap for {class_name}: {e}")
        return None

def parse_javap_output(javap_output: str) -> Dict:
    """Parse javap output to extract class information."""
    lines = javap_output.split('\n')

    result = {
        'class_name': None,
        'simple_name': None,
        'package': None,
        'class_signature': None,
        'extends': None,
        'implements': [],
        'fields': [],
        'constructors': [],
        'methods': []
    }

    # Find class declaration
    for line in lines:
        stripped = line.strip()
        if (stripped.startswith('public') or stripped.startswith('private') or stripped.startswith('protected')) and ' class ' in stripped:
            result['class_signature'] = stripped

            # Extract full class name
            class_match = re.search(r'class\s+([\w.$]+)', stripped)
            if class_match:
                result['class_name'] = class_match.group(1)
                result['simple_name'] = result['class_name'].split('.')[-1]
                result['package'] = '.'.join(result['class_name'].split('.')[:-1])

            # Extract extends
            if ' extends ' in stripped:
                extends_part = stripped.split(' extends ')[1]
                if ' implements ' in extends_part:
                    result['extends'] = extends_part.split(' implements ')[0].strip()
                else:
                    result['extends'] = extends_part.strip()

            # Extract implements
            if ' implements ' in stripped:
                implements_part = stripped.split(' implements ')[1]
                result['implements'] = [i.strip() for i in implements_part.split(',')]

            break

    # Parse members (look for section starting with {)
    in_class_body = False
    for line in lines:
        stripped = line.strip()

        if stripped == '{':
            in_class_body = True
            continue

        if not in_class_body:
            continue

        # Check if this is a method/constructor (contains parentheses) or a field
        if (stripped.startswith('private ') or stripped.startswith('public ') or stripped.startswith('protected ')) and stripped.endswith(';'):

            # If it contains '(', it's a constructor or method, not a field
            if '(' in stripped:
                # Constructors and methods
                sig = stripped.rstrip(';')

                # Check if constructor - look for class name followed by (
                # Constructors don't have a return type, so check if line doesn't start with a type
                # Constructor format: "public ClassName(params)"
                # Method format: "public ReturnType methodName(params)"
                parts_after_visibility = sig.split(maxsplit=1)
                if len(parts_after_visibility) > 1:
                    after_visibility = parts_after_visibility[1]

                    # If it contains the simple class name followed by (, it's likely a constructor
                    # Also check it doesn't have a return type (no space before the name with paren)
                    is_constructor = result['simple_name'] and f"{result['simple_name']}(" in after_visibility

                    if is_constructor:
                        result['constructors'].append({'signature': sig})
                    else:
                        result['methods'].append({'signature': sig})
                else:
                    result['methods'].append({'signature': sig})
            else:
                # It's a field (no parentheses)
                field_sig = stripped.rstrip(';')
                result['fields'].append({'signature': field_sig})

    return result

def auto_wrap_keywords(text: str, class_info: Dict) -> str:
    """Automatically wrap code keywords found in the class signature."""

    keywords = set()

    # Add the current class name
    keywords.add(class_info['simple_name'])

    # Extract class names from the signature
    signature = class_info['class_signature']

    # Extract from "extends Xxx"
    if 'extends' in signature:
        extends_part = signature.split('extends')[1].split('implements')[0] if 'implements' in signature else signature.split('extends')[1]
        # Match class names like "PluginBase" or "java.lang.Object" or generics like "Enum<PluginType>"
        for match in re.findall(r'([A-Z][a-zA-Z0-9]*)', extends_part):
            keywords.add(match)

    # Extract from "implements Xxx, Yyy"
    if 'implements' in signature:
        implements_part = signature.split('implements')[1]
        for match in re.findall(r'([A-Z][a-zA-Z0-9]*)', implements_part):
            keywords.add(match)

    # Now wrap each keyword in the text
    for keyword in keywords:
        # Use word boundaries to avoid partial matches
        text = re.sub(r'\b(' + re.escape(keyword) + r')\b', r'<code>\1</code>', text)

    return text

def call_ollama(prompt: str, class_info: Dict) -> str:
    """Call Ollama API to generate text."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {'temperature': 0.7, 'top_p': 0.9}
            },
            timeout=60
        )
        response.raise_for_status()
        description = response.json()['response'].strip()

        # Auto-wrap keywords found in the class signature
        description = auto_wrap_keywords(description, class_info)

        return description
    except Exception as e:
        print(f"    Warning: Ollama error: {e}")
        return "Description unavailable."

def generate_scripted_description(signature: str, member_type: str, class_name: str) -> str:
    """Generate simple template-based description for a member."""

    description = ""

    if member_type == 'field':
        # Just use field name, skip trying to extract type from complex generics
        parts = signature.strip().split()
        field_name = parts[-1]
        description = f"The <code>{field_name}</code> field."

    elif member_type == 'constructor':
        description = f"Creates a new instance of <code>{class_name}</code>."

    elif member_type == 'method':
        # Check if void
        if ' void ' in signature:
            # Extract method name
            paren_idx = signature.find('(')
            if paren_idx > 0:
                before_paren = signature[:paren_idx].strip().split()
                method_name = before_paren[-1]
                description = f"The <code>{method_name}()</code> method."
        else:
            # For non-void, just say it's a method - don't try to parse complex generics
            paren_idx = signature.find('(')
            if paren_idx > 0:
                before_paren = signature[:paren_idx].strip().split()
                method_name = before_paren[-1]
                description = f"The <code>{method_name}()</code> method."

    return description

def generate_class_description(class_info: Dict) -> str:
    """Generate scripted class description from signature."""

    sig = class_info['class_signature']
    name = class_info['simple_name']

    # Start building description
    desc = f"{name} is "

    # Check modifiers
    if 'abstract' in sig:
        desc += "an abstract class"
    elif 'final' in sig and 'enum' not in sig:
        desc += "a final class"
    elif 'enum' in sig or 'Enum<' in sig:
        desc += "an enum"
    elif 'interface' in sig:
        desc += "an interface"
    else:
        desc += "a class"

    # Check extends
    if 'extends' in sig:
        extends_part = sig.split('extends')[1].split('implements')[0] if 'implements' in sig else sig.split('extends')[1]
        # Extract simple class name
        match = re.search(r'([A-Z][a-zA-Z0-9]*)', extends_part)
        if match:
            parent = match.group(1)
            desc += f" that extends {parent}"

    # Check implements
    if 'implements' in sig:
        implements_part = sig.split('implements')[1]
        # Extract all interface names
        interfaces = re.findall(r'([A-Z][a-zA-Z0-9]*)', implements_part)
        if interfaces:
            if len(interfaces) == 1:
                desc += f" and implements {interfaces[0]}" if 'extends' in sig else f" that implements {interfaces[0]}"
            else:
                ifaces = ', '.join(interfaces[:-1]) + f" and {interfaces[-1]}"
                desc += f" and implements {ifaces}" if 'extends' in sig else f" that implements {ifaces}"

    desc += "."

    # Wrap class names in <code> tags
    desc = auto_wrap_keywords(desc, class_info)

    return desc

def generate_descriptions(class_info: Dict) -> Dict:
    """Generate scripted descriptions for class and members."""
    print(f"  Generating descriptions...")

    # Class description - scripted template
    class_info['description'] = generate_class_description(class_info)

    # Member descriptions - scripted (simple templates)
    for field in class_info['fields']:
        field['description'] = generate_scripted_description(field['signature'], 'field', class_info['simple_name'])

    for constructor in class_info['constructors']:
        constructor['description'] = generate_scripted_description(constructor['signature'], 'constructor', class_info['simple_name'])

    for method in class_info['methods']:
        method['description'] = generate_scripted_description(method['signature'], 'method', class_info['simple_name'])

    return class_info

def shorten_type_name(full_type: str) -> str:
    """Shorten qualified type names for display."""
    # Remove java.lang prefix
    if full_type.startswith('java.lang.'):
        return full_type.replace('java.lang.', '')

    # Get simple name for other packages
    if '.' in full_type:
        return full_type.split('.')[-1]

    return full_type

def make_type_clickable(type_str: str) -> str:
    """Convert type references to clickable HTML links."""

    # First handle Hytale classes (com.hypixel.hytale.*)
    hytale_pattern = r'\b(com\.hypixel\.hytale\.[\w.]+)\b'

    def replace_hytale_link(match):
        full_name = match.group(1)
        simple_name = full_name.split('.')[-1]
        class_file = simple_name + '.html'
        return f'<a href="{class_file}" class="type-link" data-full-name="{full_name}">{simple_name}</a>'

    result = re.sub(hytale_pattern, replace_hytale_link, type_str)

    # Then handle Java standard library classes (java.*, javax.*)
    java_pattern = r'\b(java(?:x)?\.[\w.]+)\b'

    def replace_java_link(match):
        full_name = match.group(1)
        simple_name = full_name.split('.')[-1]
        # Use # for Java stdlib links (we don't have docs for them)
        return f'<a href="#" class="type-link" data-full-name="{full_name}">{simple_name}</a>'

    result = re.sub(java_pattern, replace_java_link, result)

    return result

def generate_html(class_info: Dict) -> str:
    """Generate complete HTML page for a class."""

    simple_name = class_info['simple_name']
    package = class_info['package']

    # Build package breadcrumb
    package_parts = package.split('.')
    breadcrumb_html = ''
    for i, part in enumerate(package_parts):
        if i > 0:
            breadcrumb_html += '<span class="separator">›</span>\n'
        breadcrumb_html += f'<a href="index.html">{part}</a>\n'

    breadcrumb_html += f'<span class="separator">›</span>\n<span class="current">{simple_name}</span>'

    # Process class signature
    sig_html = make_type_clickable(class_info['class_signature'])
    sig_html = sig_html.replace('public', '<span class="modifier public">public</span>')
    sig_html = sig_html.replace('abstract', '<span class="modifier abstract">abstract</span>')
    sig_html = sig_html.replace('final', '<span class="modifier final">final</span>')
    sig_html = sig_html.replace(' class ', ' class ')

    # Generate fields HTML
    fields_html = ''
    for field in class_info['fields']:
        sig = field['signature']

        # Extract modifiers
        modifiers_html = ''
        if 'private' in sig:
            modifiers_html += '<span class="modifier private">private</span> '
            visibility_class = 'private-member'
        elif 'protected' in sig:
            modifiers_html += '<span class="modifier protected">protected</span> '
            visibility_class = 'protected-member'
        else:
            modifiers_html += '<span class="modifier public">public</span> '
            visibility_class = ''

        if 'final' in sig:
            modifiers_html += '<span class="modifier final">final</span> '
        if 'static' in sig:
            modifiers_html += '<span class="modifier static">static</span> '

        # Make type clickable
        sig_clickable = make_type_clickable(sig)

        fields_html += f'''
                    <div class="member-item {visibility_class}">
                        <div class="mb-2">
                            {modifiers_html}
                        </div>
                        <div class="member-signature">
<code class="language-java">{sig_clickable}</code>
                        </div>
                        <p class="mt-2 mb-0">{field.get('description', '')}</p>
                    </div>
'''

    if not fields_html:
        fields_html = '<p class="empty-section">No fields</p>'

    # Generate constructors HTML
    constructors_html = ''
    for constructor in class_info['constructors']:
        sig = make_type_clickable(constructor['signature'])

        constructors_html += f'''
                    <div class="member-item">
                        <div class="mb-2">
                            <span class="modifier public">public</span>
                        </div>
                        <div class="member-signature">
<code class="language-java">{sig}</code>
                        </div>
                        <p class="mt-2 mb-0">{constructor.get('description', '')}</p>
                    </div>
'''

    if not constructors_html:
        constructors_html = '<p class="empty-section">No public constructors</p>'

    # Generate methods HTML
    methods_html = ''
    for method in class_info['methods']:
        sig = method['signature']

        # Extract modifiers
        modifiers_html = ''
        if 'private' in sig:
            modifiers_html += '<span class="modifier private">private</span> '
            visibility_class = 'private-member'
        elif 'protected' in sig:
            modifiers_html += '<span class="modifier protected">protected</span> '
            visibility_class = 'protected-member'
        else:
            modifiers_html += '<span class="modifier public">public</span> '
            visibility_class = ''

        if 'final' in sig:
            modifiers_html += '<span class="modifier final">final</span> '
        if 'static' in sig:
            modifiers_html += '<span class="modifier static">static</span> '
        if 'abstract' in sig:
            modifiers_html += '<span class="modifier abstract">abstract</span> '

        sig_clickable = make_type_clickable(sig)

        methods_html += f'''
                    <div class="member-item {visibility_class}">
                        <div class="mb-2">
                            {modifiers_html}
                        </div>
                        <div class="member-signature">
<code class="language-java">{sig_clickable}</code>
                        </div>
                        <p class="mt-2 mb-0">{method.get('description', '')}</p>
                    </div>
'''

    if not methods_html:
        methods_html = '<p class="empty-section">No methods</p>'

    # Full HTML template
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{simple_name} - Hytale Plugin API</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Prism.js for syntax highlighting (dark theme) -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">

    <!-- Custom styles -->
    <link href="../assets/css/javadoc-style.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <div class="navbar-breadcrumb">
                {breadcrumb_html}
            </div>
            <a href="https://github.com/Henry-Bonikowsky/hytale-plugin-docs" class="navbar-github" target="_blank" title="View on GitHub">
                <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
            </a>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- API Navigation Sidebar -->
            <div class="col-auto">
                <div class="sidebar">
                    <!-- Search -->
                    <div class="sidebar-search">
                        <input type="text" class="form-control form-control-sm" placeholder="Search classes...">
                    </div>

                    <!-- Package Tree -->
                    <nav class="sidebar-nav">
                        <div class="package-group">
                            <div class="package-title">com.hypixel.hytale.server.core</div>

                            <div class="package-section">
                                <div class="package-name" data-toggle="collapse">
                                    <span class="chevron">▼</span> plugin
                                </div>
                                <div class="package-classes">
                                    <a href="JavaPlugin.html" class="class-link">JavaPlugin</a>
                                    <a href="PluginBase.html" class="class-link">PluginBase</a>
                                    <a href="PluginClassLoader.html" class="class-link">PluginClassLoader</a>
                                    <a href="JavaPluginInit.html" class="class-link">JavaPluginInit</a>
                                    <a href="PluginType.html" class="class-link">PluginType</a>
                                </div>
                            </div>

                            <div class="package-section">
                                <div class="package-name" data-toggle="collapse">
                                    <span class="chevron">▼</span> asset
                                </div>
                                <div class="package-classes">
                                    <a href="AssetModule.html" class="class-link">AssetModule</a>
                                    <a href="AssetPackRegisterEvent.html" class="class-link">AssetPackRegisterEvent</a>
                                </div>
                            </div>

                            <div class="package-section">
                                <div class="package-name" data-toggle="collapse">
                                    <span class="chevron">▼</span> event
                                </div>
                                <div class="package-classes">
                                    <a href="EventRegistry.html" class="class-link">EventRegistry</a>
                                </div>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>

            <!-- Main content -->
            <div class="col">
                <div class="content-wrapper">
                <!-- Class header -->
                <div class="class-header" id="overview">
                    <h1 class="class-name">{simple_name}</h1>

                    <div class="class-signature">
<pre><code class="language-java">{sig_html}</code></pre>
                    </div>

                    <p class="mt-3">
                        {class_info.get('description', '')}
                    </p>
                </div>

                <!-- Visibility toggle -->
                <div class="visibility-toggle">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="show-private">
                        <label class="form-check-label" for="show-private">
                            Show private/protected members
                        </label>
                    </div>
                </div>

                <!-- Fields section -->
                <div class="member-section" id="fields">
                    <h2>Fields</h2>
                    {fields_html}
                </div>

                <!-- Constructors section -->
                <div class="member-section" id="constructors">
                    <h2>Constructors</h2>
                    {constructors_html}
                </div>

                <!-- Methods section -->
                <div class="member-section" id="methods">
                    <h2>Methods</h2>
                    {methods_html}
                </div>

                <!-- Footer -->
                <div class="docs-footer">
                    Generated from <code>hytale-server-2026.01.15.jar</code> using javap.<br>
                    Not affiliated with Hypixel Studios.
                </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Prism.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>

    <!-- Custom JS -->
    <script src="../assets/js/javadoc-ui.js"></script>
</body>
</html>
'''

    return html

def process_class(class_name: str):
    """Process a single class: extract, generate descriptions, create HTML."""
    simple_name = class_name.split('.')[-1]
    print(f"\n- Processing {simple_name}...")

    # Extract javap output
    print(f"  Extracting javap...")
    javap_output = extract_javap(class_name)
    if not javap_output:
        print(f"  Failed: Failed to extract javap for {class_name}")
        return False

    # Parse
    print(f"  Parsing...")
    class_info = parse_javap_output(javap_output)
    if not class_info['simple_name']:
        print(f"  Failed: Failed to parse class info")
        return False

    # Generate descriptions
    class_info = generate_descriptions(class_info)

    # Generate HTML
    print(f"  Generating HTML...")
    html = generate_html(class_info)

    # Write HTML file
    output_file = OUTPUT_DIR / f"{simple_name}.html"
    output_file.write_text(html, encoding='utf-8')

    print(f"  Done: Saved to {output_file.name}")
    return True

def main():
    """Main entry point."""

    # Test classes
    test_classes = [
        "com.hypixel.hytale.server.core.plugin.PluginBase",
        "com.hypixel.hytale.server.core.plugin.PluginClassLoader",
        "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
        "com.hypixel.hytale.server.core.plugin.PluginType",
        "com.hypixel.hytale.server.core.asset.AssetModule",
        "com.hypixel.hytale.server.core.asset.AssetPackRegisterEvent",
    ]

    # Use command line args if provided, otherwise use test classes
    if len(sys.argv) > 2 and sys.argv[1] == '--file':
        # Read from file
        with open(sys.argv[2], 'r') as f:
            classes_to_process = [line.strip() for line in f if line.strip()]
    elif len(sys.argv) > 1:
        classes_to_process = sys.argv[1:]
    else:
        classes_to_process = test_classes

    print(f"Hytale Plugin API Documentation Generator")
    print(f"Processing {len(classes_to_process)} classes...")

    success_count = 0
    fail_count = 0

    for class_name in classes_to_process:
        if process_class(class_name):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"SUCCESS: Complete: {success_count} succeeded, {fail_count} failed")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
