#!/usr/bin/env python3
"""
Script to format HTML template files for better readability.
"""

import os
from bs4 import BeautifulSoup

def format_html_file(file_path):
    """Format an HTML file with proper indentation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Format with proper indentation
        formatted_html = soup.prettify()
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_html)
            
        print(f"✓ Formatted: {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"✗ Error formatting {file_path}: {str(e)}")

def main():
    """Format all template files."""
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        print(f"Templates directory not found: {templates_dir}")
        return
    
    # Get all .htm files in templates directory
    template_files = [f for f in os.listdir(templates_dir) if f.endswith('.htm')]
    
    if not template_files:
        print("No .htm files found in templates directory")
        return
    
    print(f"Formatting {len(template_files)} template files...")
    
    for template_file in sorted(template_files):
        file_path = os.path.join(templates_dir, template_file)
        format_html_file(file_path)
    
    print("\nFormatting completed!")

if __name__ == '__main__':
    main()
