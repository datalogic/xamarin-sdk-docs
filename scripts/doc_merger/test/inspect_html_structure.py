#!/usr/bin/env python3
"""
Simple test to inspect the BarcodeManager HTML structure.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

def inspect_barcode_manager_html():
    """Inspect the BarcodeManager HTML file structure."""
    
    # Path to the BarcodeManager HTML file
    html_file = Path(__file__).parent.parent.parent.parent / "generated-docs" / "javadoc" / "com" / "datalogic" / "decode" / "BarcodeManager.html"
    
    print(f"Inspecting file: {html_file}")
    
    if not html_file.exists():
        print(f"ERROR: File not found: {html_file}")
        return
    
    # Read and parse the HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    print("\n" + "="*60)
    print("SEARCHING FOR CLASS DESCRIPTION")
    print("="*60)
    
    # Try the main selector used in the code
    class_desc = soup.select_one('section.class-description div.block')
    print(f"1. section.class-description div.block: {'FOUND' if class_desc else 'NOT FOUND'}")
    if class_desc:
        print(f"   Content: {class_desc.get_text(strip=True)[:200]}...")
    
    # Try alternative selectors
    selectors = [
        'div.description div.block',
        '.classDescription', 
        '.summary',
        'div.block',
        'section.class-description',
        'div.type-signature + div.block',
        '.class-description .block'
    ]
    
    for i, selector in enumerate(selectors, 2):
        elements = soup.select(selector)
        print(f"{i}. {selector}: {'FOUND' if elements else 'NOT FOUND'} ({len(elements)} elements)")
        if elements:
            for j, elem in enumerate(elements[:2]):  # Show first 2 elements
                text = elem.get_text(strip=True)
                if text:
                    print(f"   Element {j+1}: {text[:150]}...")
    
    print("\n" + "="*60)
    print("EXAMINING HTML STRUCTURE")
    print("="*60)
    
    # Look for sections
    sections = soup.find_all('section')
    print(f"Found {len(sections)} <section> elements:")
    for i, section in enumerate(sections):
        class_attr = section.get('class', [])
        id_attr = section.get('id', '')
        print(f"  Section {i+1}: class={class_attr}, id='{id_attr}'")
        
        # Look for div.block inside this section
        blocks = section.select('div.block')
        if blocks:
            print(f"    Contains {len(blocks)} div.block elements:")
            for j, block in enumerate(blocks[:2]):
                text = block.get_text(strip=True)
                if text:
                    print(f"      Block {j+1}: {text[:100]}...")
    
    # Look for all div.block elements
    print(f"\nAll div.block elements in document:")
    all_blocks = soup.select('div.block')
    print(f"Found {len(all_blocks)} div.block elements:")
    for i, block in enumerate(all_blocks[:5]):  # Show first 5
        text = block.get_text(strip=True)
        if text:
            print(f"  Block {i+1}: {text[:100]}...")
        
    # Look specifically for class description area
    print(f"\nLooking for main content area...")
    main_content = soup.select_one('main')
    if main_content:
        print("Found <main> element")
        # Look for the description in main
        desc_blocks = main_content.select('div.block')
        print(f"Found {len(desc_blocks)} div.block elements in main:")
        for i, block in enumerate(desc_blocks[:3]):
            text = block.get_text(strip=True)
            if text and len(text) > 20:  # Only show substantial content
                print(f"  Main Block {i+1}: {text[:150]}...")
    
    # Save a simplified structure to a file for analysis
    output_file = Path(__file__).parent / "test-output" / "html_structure_analysis.txt"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("BarcodeManager HTML Structure Analysis\n")
        f.write("="*50 + "\n\n")
        
        f.write("All div.block elements:\n")
        for i, block in enumerate(all_blocks):
            text = block.get_text(strip=True)
            parent = block.parent
            parent_info = f"{parent.name}"
            if parent.get('class'):
                parent_info += f".{'.'.join(parent.get('class'))}"
            if parent.get('id'):
                parent_info += f"#{parent.get('id')}"
                
            f.write(f"\nBlock {i+1} (parent: {parent_info}):\n")
            f.write(f"  Text: {text}\n")
            f.write(f"  Length: {len(text)}\n")
    
    print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == "__main__":
    inspect_barcode_manager_html()
