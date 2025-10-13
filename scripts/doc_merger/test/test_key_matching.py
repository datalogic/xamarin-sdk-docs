#!/usr/bin/env python3
"""
Simple test to verify the key matching issue.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the doc_merger module
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from doc_merger import DocMerger

def test_key_matching():
    """Test the key matching issue."""
    
    # Set up paths
    base_dir = Path(__file__).parent.parent.parent.parent
    mdoc_path = base_dir / "generated-docs" / "mdoc"
    javadoc_path = base_dir / "generated-docs" / "javadoc"
    html_path = base_dir / "html"
    output_path = Path(__file__).parent / "test-output"
    
    # Create DocMerger instance
    merger = DocMerger(
        mdoc_path=str(mdoc_path),
        javadoc_path=str(javadoc_path),
        html_template_path=str(html_path),
        output_path=str(output_path),
        version="1.45"
    )
    
    # Load javadoc content
    merger.load_javadoc_content()
    
    print("Testing key matching issue:")
    print("-" * 40)
    
    # Show actual keys
    barcode_keys = [k for k in merger.javadoc_content.keys() if 'BarcodeManager' in k]
    print(f"Actual keys containing 'BarcodeManager': {barcode_keys}")
    
    # Test the problematic conversion
    test_class_name = "com.datalogic.decode.BarcodeManager"
    
    # This is what the current code does (problematic)
    java_class_name_lowercase = test_class_name.lower()
    print(f"\nCurrent code converts '{test_class_name}' to '{java_class_name_lowercase}'")
    print(f"Key exists in javadoc_content? {java_class_name_lowercase in merger.javadoc_content}")
    
    # This is what it should do (preserve case)
    java_class_name_preserved = test_class_name
    print(f"\nShould look for '{java_class_name_preserved}'")
    print(f"Key exists in javadoc_content? {java_class_name_preserved in merger.javadoc_content}")
    
    # Test different input formats
    test_inputs = [
        "com.datalogic.decode.BarcodeManager",
        "com/datalogic/decode/BarcodeManager", 
        "Com.Datalogic.Decode.BarcodeManager",
        "Com/Datalogic/Decode/BarcodeManager"
    ]
    
    print(f"\nTesting different input formats:")
    for input_name in test_inputs:
        # Convert path separators but preserve case
        normalized = input_name.replace('/', '.').replace('\\', '.')
        exists = normalized in merger.javadoc_content
        print(f"  '{input_name}' -> '{normalized}' -> {'FOUND' if exists else 'NOT FOUND'}")

if __name__ == "__main__":
    test_key_matching()
