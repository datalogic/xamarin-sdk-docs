"""
Helper module for handling HTML templates for the documentation merger.

This module provides functions to load and use static HTML templates for different documentation types.
"""

import os
import sys
import logging

# Try to import BeautifulSoup, exit with error if not available
try:
    from bs4 import BeautifulSoup
    # Use default parser
    PARSER = "html.parser"
except ImportError:
    print("Error: beautifulsoup4 is not installed. Please install it using:")
    print("pip install beautifulsoup4")
    sys.exit(1)

logger = logging.getLogger(__name__)

# Template file mappings - these are our clean, static templates
TEMPLATE_FILES = {
    'class': 'class_template.htm',
    'methods': 'methods_template.htm', 
    'properties': 'properties_template.htm',
    'method': 'method_template.htm',
    'property': 'property_template.htm',
    'field': 'field_template.htm',
    'overload': 'overload_template.htm',
    'namespace': 'namespace_template.htm'
}

def get_template(template_type, templates_dir='templates'):
    """
    Load a static template file and return its content.
    
    Args:
        template_type: Type of template ('class', 'methods', 'properties', 'method', 'property', 'field', 'overload')
        templates_dir: Directory containing template files
        
    Returns:
        BeautifulSoup object of the template, or None if not found
    """
    try:
        if template_type not in TEMPLATE_FILES:
            logger.error(f"Unknown template type: {template_type}")
            return None
            
        template_file = TEMPLATE_FILES[template_type]
        template_path = os.path.join(templates_dir, template_file)
        
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            return None
            
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, PARSER)
        logger.debug(f"Successfully loaded template: {template_type}")
        return soup
        
    except Exception as e:
        logger.error(f"Error loading template {template_type}: {str(e)}")
        return None

def get_template_content(template_type, templates_dir='templates'):
    """
    Load a template file and return its raw content as string.
    
    Args:
        template_type: Type of template ('class', 'methods', 'properties', 'method', 'property', 'field', 'overload')
        templates_dir: Directory containing template files
        
    Returns:
        Raw HTML content as string, or None if not found
    """
    try:
        if template_type not in TEMPLATE_FILES:
            logger.error(f"Unknown template type: {template_type}")
            return None
            
        template_file = TEMPLATE_FILES[template_type]
        template_path = os.path.join(templates_dir, template_file)
        
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            return None
            
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        logger.debug(f"Successfully loaded template content: {template_type}")
        return html_content
        
    except Exception as e:
        logger.error(f"Error loading template content {template_type}: {str(e)}")
        return None

def replace_placeholders(template_content, replacements):
    """
    Replace placeholders in template content with actual values.
    
    Args:
        template_content: Raw HTML template content with {{PLACEHOLDER}} markers
        replacements: Dictionary of placeholder->value mappings
        
    Returns:
        HTML content with placeholders replaced
    """
    try:
        content = template_content
        
        for placeholder, value in replacements.items():
            placeholder_marker = f"{{{{{placeholder}}}}}"
            if placeholder_marker in content:
                content = content.replace(placeholder_marker, str(value))
                logger.debug(f"Replaced {placeholder_marker} with value")
        
        return content
        
    except Exception as e:
        logger.error(f"Error replacing placeholders: {str(e)}")
        return template_content

def validate_templates(templates_dir='templates'):
    """
    Validate that all required template files exist.
    
    Args:
        templates_dir: Directory containing template files
        
    Returns:
        Boolean indicating if all templates are available
    """
    try:
        missing_templates = []
        
        for template_type, template_file in TEMPLATE_FILES.items():
            template_path = os.path.join(templates_dir, template_file)
            if not os.path.exists(template_path):
                missing_templates.append(template_file)
        
        if missing_templates:
            logger.error(f"Missing template files: {', '.join(missing_templates)}")
            return False
        
        logger.info(f"All {len(TEMPLATE_FILES)} templates found in {templates_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error validating templates: {str(e)}")
        return False
