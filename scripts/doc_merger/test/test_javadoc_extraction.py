#!/usr/bin/env python3
"""
Test script to debug javadoc content extraction.
This script tests the load_javadoc_content and extract_javadoc_description functions
using the BarcodeManager files as test data.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path so we can import the doc_merger module
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the DocMerger class
from doc_merger import DocMerger

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_javadoc_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_javadoc_extraction():
    """Test the javadoc extraction functions."""
    
    # Set up paths - go up 3 levels from test directory to get to project root
    base_dir = Path(__file__).parent.parent.parent.parent
    mdoc_path = base_dir / "generated-docs" / "mdoc"
    javadoc_path = base_dir / "generated-docs" / "javadoc"
    html_path = base_dir / "html"
    output_path = Path(__file__).parent / "test-output"
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    print(f"Base directory: {base_dir}")
    print(f"MDDoc path: {mdoc_path}")
    print(f"JavaDoc path: {javadoc_path}")
    print(f"HTML template path: {html_path}")
    print(f"Output path: {output_path}")
    
    # Check if paths exist
    if not mdoc_path.exists():
        print(f"ERROR: MDDoc path does not exist: {mdoc_path}")
        return
    if not javadoc_path.exists():
        print(f"ERROR: JavaDoc path does not exist: {javadoc_path}")
        return
    if not html_path.exists():
        print(f"ERROR: HTML template path does not exist: {html_path}")
        return
    
    # Check specific test files
    barcode_manager_xml = mdoc_path / "Com.Datalogic.Decode" / "BarcodeManager.xml"
    barcode_manager_html = javadoc_path / "com" / "datalogic" / "decode" / "BarcodeManager.html"
    
    print(f"\nChecking test files:")
    print(f"MDDoc XML file: {barcode_manager_xml} - {'EXISTS' if barcode_manager_xml.exists() else 'MISSING'}")
    print(f"JavaDoc HTML file: {barcode_manager_html} - {'EXISTS' if barcode_manager_html.exists() else 'MISSING'}")
    
    if not barcode_manager_xml.exists():
        print(f"ERROR: BarcodeManager XML file not found: {barcode_manager_xml}")
        return
    if not barcode_manager_html.exists():
        print(f"ERROR: BarcodeManager HTML file not found: {barcode_manager_html}")
        return
    
    # Create DocMerger instance
    merger = DocMerger(
        mdoc_path=str(mdoc_path),
        javadoc_path=str(javadoc_path),
        html_template_path=str(html_path),
        output_path=str(output_path),
        version="1.45"
    )
    
    print("\n" + "="*60)
    print("TESTING load_javadoc_content() function")
    print("="*60)
    
    # Test load_javadoc_content
    merger.load_javadoc_content()
    
    print(f"\nLoaded {len(merger.javadoc_content)} JavaDoc files")
    print("\nFirst 10 keys in javadoc_content:")
    for i, key in enumerate(sorted(merger.javadoc_content.keys())[:10]):
        print(f"  {i+1}: {key}")
    
    # Look specifically for BarcodeManager related keys
    barcode_keys = [key for key in merger.javadoc_content.keys() if 'barcode' in key.lower()]
    print(f"\nKeys containing 'barcode' ({len(barcode_keys)}):")
    for key in barcode_keys:
        print(f"  - {key}")
    
    print("\n" + "="*60)
    print("TESTING extract_javadoc_description() function")
    print("="*60)
    
    # Test extract_javadoc_description for different class name formats
    test_class_names = [
        "com.datalogic.decode.BarcodeManager",
        "com/datalogic/decode/BarcodeManager",
        "Com.Datalogic.Decode.BarcodeManager",
        "Com/Datalogic/Decode/BarcodeManager",
        "com.datalogic.decode.barcodemanager",
        "com/datalogic/decode/barcodemanager"
    ]
    
    for class_name in test_class_names:
        print(f"\n--- Testing class name: '{class_name}' ---")
        summary, remarks = merger.extract_javadoc_description(class_name)
        print(f"Summary: {summary[:100] if summary else 'EMPTY'}{'...' if len(summary) > 100 else ''}")
        print(f"Remarks: {remarks[:100] if remarks else 'EMPTY'}{'...' if len(remarks) > 100 else ''}")
    
    # Test with a specific member
    print(f"\n--- Testing member extraction: startDecode ---")
    summary, remarks = merger.extract_javadoc_description("com.datalogic.decode.BarcodeManager", "startDecode")
    print(f"Member Summary: {summary[:100] if summary else 'EMPTY'}{'...' if len(summary) > 100 else ''}")
    print(f"Member Remarks: {remarks[:100] if remarks else 'EMPTY'}{'...' if len(remarks) > 100 else ''}")
    
    print("\n" + "="*60)
    print("INSPECTING ACTUAL HTML CONTENT")
    print("="*60)
    
    # Let's inspect the actual HTML content for BarcodeManager
    if "com.datalogic.decode.barcodemanager" in merger.javadoc_content:
        soup = merger.javadoc_content["com.datalogic.decode.barcodemanager"]
        print("\nFound BarcodeManager in javadoc_content!")
        
        # Check for class description
        class_desc = soup.select_one('section.class-description div.block')
        if class_desc:
            print(f"Class description found: {class_desc.get_text(strip=True)[:200]}...")
        else:
            print("No class description found with selector 'section.class-description div.block'")
            
        # Try alternative selectors
        alt_selectors = ['div.description div.block', '.classDescription', '.summary', 'div.block']
        for selector in alt_selectors:
            alt_desc = soup.select(selector)
            if alt_desc:
                print(f"Alternative selector '{selector}' found {len(alt_desc)} elements")
                for i, elem in enumerate(alt_desc[:2]):  # Show first 2 elements
                    text = elem.get_text(strip=True)
                    print(f"  Element {i+1}: {text[:100]}{'...' if len(text) > 100 else ''}")
    else:
        print("BarcodeManager not found in javadoc_content")
        # Show what keys are available that might match
        possible_keys = [k for k in merger.javadoc_content.keys() if 'barcode' in k.lower() or 'manager' in k.lower()]
        print(f"Possible matching keys: {possible_keys}")
    
    # Save debug information to a file
    debug_file = output_path / "javadoc_extraction_debug.txt"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write("JavaDoc Extraction Debug Information\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total JavaDoc files loaded: {len(merger.javadoc_content)}\n\n")
        
        f.write("All loaded keys:\n")
        for key in sorted(merger.javadoc_content.keys()):
            f.write(f"  - {key}\n")
        
        f.write("\nBarcode-related keys:\n")
        for key in barcode_keys:
            f.write(f"  - {key}\n")
        
        # Test extractions
        f.write("\nExtraction Results:\n")
        for class_name in test_class_names:
            summary, remarks = merger.extract_javadoc_description(class_name)
            f.write(f"\nClass: {class_name}\n")
            f.write(f"Summary: {summary}\n")
            f.write(f"Remarks: {remarks}\n")
    
    print(f"\nDebug information saved to: {debug_file}")
    print("Test completed!")

if __name__ == "__main__":
    test_javadoc_extraction()
