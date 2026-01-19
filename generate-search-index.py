#!/usr/bin/env python3
"""
Generate search index JSON file with all classes and their methods
"""
import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_methods_from_html(html_path):
    """Extract method names from a class HTML file"""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    methods = []

    # Find all method descriptions in the Methods section
    method_items = soup.find_all('div', class_='member-item')

    for item in method_items:
        # Check if this is in the methods section (not fields or constructors)
        parent_section = item.find_parent('div', class_='member-section')
        if parent_section and parent_section.find('h2'):
            section_title = parent_section.find('h2').get_text().strip()
            if section_title == 'Methods':
                # Extract method name from the signature
                signature = item.find('div', class_='member-signature')
                if signature:
                    code = signature.find('code')
                    if code:
                        # Parse method signature to extract method name
                        # Example: "public Value get(String)" -> "get"
                        # Example: "public static ... create()" -> "create"
                        sig_text = code.get_text()

                        # Find method name - it's the identifier before the opening parenthesis
                        # Match: word followed by (
                        match = re.search(r'\b(\w+)\s*\(', sig_text)
                        if match:
                            method_name = match.group(1)
                            # Skip constructor names (same as class name) - we'll handle those separately
                            methods.append(method_name)

    return list(set(methods))  # Remove duplicates

def generate_search_index(docs_dir):
    """Generate search index from all class HTML files"""
    classes_dir = Path(docs_dir) / 'classes'

    index = []

    # Get all HTML files except index.html
    html_files = [f for f in classes_dir.glob('*.html') if f.name != 'index.html']

    print(f"Processing {len(html_files)} class files...")

    for i, html_file in enumerate(html_files, 1):
        if i % 500 == 0:
            print(f"  Processed {i}/{len(html_files)}...")

        class_name = html_file.stem  # Filename without .html

        try:
            methods = extract_methods_from_html(html_file)

            # Add class entry
            index.append({
                'type': 'class',
                'name': class_name,
                'file': f'classes/{class_name}.html'
            })

            # Add method entries
            for method in methods:
                index.append({
                    'type': 'method',
                    'name': method,
                    'class': class_name,
                    'file': f'classes/{class_name}.html#methods'
                })
        except Exception as e:
            print(f"Error processing {class_name}: {e}")

    print(f"Generated index with {len(index)} entries")
    return index

def main():
    docs_dir = Path(__file__).parent / 'docs'

    print("Generating search index...")
    index = generate_search_index(docs_dir)

    # Save to JSON file
    output_file = docs_dir / 'assets' / 'search-index.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, separators=(',', ':'))

    print(f"Search index saved to {output_file}")
    print(f"Index size: {output_file.stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    main()
