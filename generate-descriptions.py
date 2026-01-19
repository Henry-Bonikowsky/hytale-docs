#!/usr/bin/env python3
"""
Generate AI-powered descriptions for Hytale API documentation.

Parses javap output and uses Ollama (Llama) to generate Stripe-quality
documentation descriptions for classes, methods, and fields.
"""

import json
import re
import sys
import requests
from pathlib import Path

def parse_javap_output(javap_file):
    """
    Parse javap output to extract class signature, fields, constructors, and methods.
    Returns a structured dict with all class members.
    """
    content = javap_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    result = {
        'class_name': None,
        'class_signature': None,
        'extends': None,
        'implements': [],
        'fields': [],
        'constructors': [],
        'methods': []
    }

    # Find class declaration line (e.g., "public abstract class com.hypixel.hytale.server.core.plugin.JavaPlugin extends ...")
    class_line = None
    for line in lines:
        if line.strip().startswith('public') and ' class ' in line:
            class_line = line.strip()
            break

    if class_line:
        # Extract class name
        if ' extends ' in class_line:
            class_part = class_line.split(' extends ')[0]
            result['extends'] = class_line.split(' extends ')[1].split(' implements ')[0].strip()
        else:
            class_part = class_line.split(' implements ')[0] if ' implements ' in class_line else class_line

        # Get simple class name
        class_match = re.search(r'class\s+([\w.$]+)', class_part)
        if class_match:
            full_name = class_match.group(1)
            result['class_name'] = full_name.split('.')[-1]

        result['class_signature'] = class_line

        # Extract implements
        if ' implements ' in class_line:
            implements_part = class_line.split(' implements ')[1]
            result['implements'] = [i.strip() for i in implements_part.split(',')]

    # Parse members - look for the section starting with {
    in_class_body = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == '{':
            in_class_body = True
            continue

        if not in_class_body:
            continue

        # Look for field declarations (private/public/protected followed by type and name, ending with ;)
        if (stripped.startswith('private ') or stripped.startswith('public ') or stripped.startswith('protected ')) and stripped.endswith(';'):
            field_sig = stripped.rstrip(';')
            parts = field_sig.split()
            if len(parts) >= 3:
                result['fields'].append({
                    'signature': field_sig,
                    'raw': field_sig
                })

        # Look for method/constructor declarations (have parentheses)
        if (stripped.startswith('public ') or stripped.startswith('private ') or stripped.startswith('protected ')) and '(' in stripped and ');' in stripped:
            sig = stripped.rstrip(';')

            # Check if constructor (contains class name)
            is_constructor = result['class_name'] and result['class_name'] in sig and ' ' + result['class_name'] + '(' in sig

            if is_constructor:
                result['constructors'].append({
                    'signature': sig,
                    'raw': sig
                })
            else:
                result['methods'].append({
                    'signature': sig,
                    'raw': sig
                })

    return result

def call_ollama(prompt, model="llama3.2"):
    """Call Ollama API to generate text."""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return "Description unavailable."

def generate_class_description(class_info):
    """Generate a description for the entire class using Ollama."""
    prompt = f"""You are writing API documentation for Hytale server plugins.

Class: {class_info['class_name']}
Signature: {class_info['class_signature']}

Generate a clear, professional 2-3 sentence description of what this class does and when developers should use it.
Write in the style of Stripe API documentation - be helpful, actionable, and context-rich.

Return ONLY the description text, no extra formatting or preamble."""

    return call_ollama(prompt)

def generate_member_description(member_type, signature, class_context):
    """Generate a description for a field, constructor, or method."""
    prompt = f"""You are writing API documentation for Hytale server plugins.

Class context: {class_context['class_name']}
Member type: {member_type}
Signature: {signature}

Generate a clear, professional 1-2 sentence description explaining what this {member_type} does.
Write in the style of Stripe API documentation - be specific, helpful, and actionable.
For methods, explain what it returns and when to use it.
For fields, explain what data it holds and its purpose.
For constructors, explain when it's called and what it initializes.

Return ONLY the description text, no extra formatting or preamble."""

    return call_ollama(prompt)

def generate_documentation(javap_file):
    """Generate complete documentation for a class."""
    print(f"Parsing {javap_file.name}...")
    class_info = parse_javap_output(javap_file)

    if not class_info['class_name']:
        print(f"Error: Could not parse class from {javap_file}")
        return None

    print(f"Generating descriptions for {class_info['class_name']}...")

    # Generate class description
    print("  - Class description...")
    class_info['description'] = generate_class_description(class_info)

    # Generate field descriptions
    for field in class_info['fields']:
        print(f"  - Field: {field['signature'][:50]}...")
        field['description'] = generate_member_description(
            'field', field['signature'], class_info
        )

    # Generate constructor descriptions
    for constructor in class_info['constructors']:
        print(f"  - Constructor")
        constructor['description'] = generate_member_description(
            'constructor', constructor['signature'], class_info
        )

    # Generate method descriptions
    for method in class_info['methods']:
        print(f"  - Method: {method['signature'][:60]}...")
        method['description'] = generate_member_description(
            'method', method['signature'], class_info
        )

    return class_info

def main():
    # Process JavaPlugin.txt as test
    test_file = Path(__file__).parent / 'JavaPlugin.txt'
    if not test_file.exists():
        print(f"Error: {test_file} not found")
        sys.exit(1)

    # Generate documentation
    docs = generate_documentation(test_file)

    if docs:
        # Save to JSON
        output_file = Path(__file__).parent / 'descriptions.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2)

        print(f"\nDescriptions saved to {output_file}")
        print(f"  Class: {docs['class_name']}")
        print(f"  Fields: {len(docs['fields'])}")
        print(f"  Constructors: {len(docs['constructors'])}")
        print(f"  Methods: {len(docs['methods'])}")
    else:
        print("Failed to generate documentation")
        sys.exit(1)

if __name__ == '__main__':
    main()
