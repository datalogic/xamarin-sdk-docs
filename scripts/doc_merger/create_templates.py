#!/usr/bin/env python3
"""
Script to create static template files from existing HTML documentation.
This is a one-time setup script to create reusable templates.
"""

import os
import sys
import logging
from template_helper import create_templates_from_existing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to create templates."""
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    html_dir = os.path.join(project_root, 'html')
    templates_dir = os.path.join(script_dir, 'templates')
    
    print(f"HTML directory: {html_dir}")
    print(f"Templates directory: {templates_dir}")
    
    # Check if HTML directory exists
    if not os.path.exists(html_dir):
        print(f"Error: HTML directory not found: {html_dir}")
        sys.exit(1)
    
    # Create templates
    print("Creating static template files...")
    create_templates_from_existing(html_dir, templates_dir)
    print("Template creation completed!")

if __name__ == '__main__':
    main()
