#!/usr/bin/env python3
"""
Main runner script for Datalogic Xamarin SDK Documentation Merger.

This script orchestrates the entire process of merging mdoc and javadoc documentation
and generating the final HTML documentation files.
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("doc_merger.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_templates(templates_dir):
    """Validate that all required templates exist."""
    try:
        from template_helper import validate_templates
        
        logger.info(f"Validating templates in {templates_dir}...")
        if not validate_templates(templates_dir):
            logger.error("Template validation failed. Please ensure all template files are present.")
            sys.exit(1)
        
        logger.info("Template validation successful.")
        
    except Exception as e:
        logger.error(f"Error validating templates: {str(e)}")
        sys.exit(1)

def merge_documentation(mdoc_path, javadoc_path, templates_dir, output_path, version):
    """Merge documentation and generate HTML files."""
    try:
        from doc_merger import DocMerger
        
        logger.info("Starting documentation merge...")
        merger = DocMerger(
            mdoc_path=mdoc_path,
            javadoc_path=javadoc_path,
            html_template_path=templates_dir,
            output_path=output_path,
            version=version
        )
        
        # Load javadoc content
        merger.load_javadoc_content()
        
        # Process mdoc files
        merger.process_mdoc_files()
        
        logger.info("Documentation merge complete.")
        
    except Exception as e:
        logger.error(f"Error merging documentation: {str(e)}")
        sys.exit(1)

def copy_static_files(source_dir, output_dir):
    """Copy static files (CSS, JS, images) to the output directory."""
    try:
        from html_helper import copy_static_assets
        
        logger.info(f"Copying static assets from {source_dir}...")
        copy_static_assets(source_dir, output_dir)
        
    except Exception as e:
        logger.error(f"Error copying static files: {str(e)}")
        sys.exit(1)

def update_readme(version):
    """Update the README.md file with the new version number."""
    try:
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'README.md')
        
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Replace version number in README
            updated_content = content.replace('1.32', version)
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            logger.info(f"Updated README.md with version {version}")
        
    except Exception as e:
        logger.error(f"Error updating README: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Merge and generate Xamarin SDK documentation.')
    parser.add_argument('--mdoc', required=True, help='Path to mdoc files')
    parser.add_argument('--javadoc', required=True, help='Path to javadoc files')
    parser.add_argument('--html', required=True, help='Path to existing HTML files')
    parser.add_argument('--output', required=True, help='Output directory for merged documentation')
    parser.add_argument('--version', required=True, help='SDK version number')
    parser.add_argument('--skip-install', action='store_true', help='Skip installation of packages')
    
    args = parser.parse_args()
    
    # Create absolute paths
    mdoc_path = os.path.abspath(args.mdoc)
    javadoc_path = os.path.abspath(args.javadoc)
    html_path = os.path.abspath(args.html)
    output_path = os.path.abspath(args.output)
    
    # Create temporary directories
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    # Create directories if they don't exist
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)
    
    
    # Validate that our static templates exist
    validate_templates(templates_dir)
    
    # Merge documentation
    merge_documentation(mdoc_path, javadoc_path, templates_dir, output_path, args.version)
    
    # Copy static files
    copy_static_files(html_path, output_path)
    
    # Update README
    update_readme(args.version)
    
    # Clean up temporary files
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    logger.info(f"Documentation update to version {args.version} complete.")
    logger.info(f"Output files are in {output_path}")

if __name__ == "__main__":
    main()
