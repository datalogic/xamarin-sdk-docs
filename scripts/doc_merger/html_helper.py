"""
Helper module for generating HTML documentation.

This module provides functions to generate HTML documentation files from the merged information.
"""

import os
import logging
import html
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_class_html(type_info, template_path, output_path, sdk_version):
    """
    Generate an HTML file for a class.
    
    Args:
        type_info: Dictionary containing class information
        template_path: Path to the HTML template file
        output_path: Path to write the output HTML
        sdk_version: SDK version string
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        output_html = template
        output_html = output_html.replace('{{TYPE_NAME}}', type_info['name'])
        output_html = output_html.replace('{{FULL_NAME}}', type_info['full_name'])
        output_html = output_html.replace('{{SUMMARY}}', html.escape(type_info['summary']))
        output_html = output_html.replace('{{REMARKS}}', html.escape(type_info['remarks']))
        output_html = output_html.replace('{{VERSION}}', sdk_version)
        output_html = output_html.replace('{{YEAR}}', str(datetime.now().year))
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        logger.info(f"Generated {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating class HTML: {str(e)}")

def generate_member_html(type_info, member_info, template_path, output_path, sdk_version):
    """
    Generate an HTML file for a class member.
    
    Args:
        type_info: Dictionary containing class information
        member_info: Dictionary containing member information
        template_path: Path to the HTML template file
        output_path: Path to write the output HTML
        sdk_version: SDK version string
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        output_html = template
        output_html = output_html.replace('{{TYPE_NAME}}', type_info['name'])
        output_html = output_html.replace('{{FULL_NAME}}', type_info['full_name'])
        output_html = output_html.replace('{{MEMBER_NAME}}', member_info['name'])
        output_html = output_html.replace('{{MEMBER_TYPE}}', member_info['type'])
        output_html = output_html.replace('{{SUMMARY}}', html.escape(member_info['summary']))
        output_html = output_html.replace('{{REMARKS}}', html.escape(member_info['remarks']))
        output_html = output_html.replace('{{VERSION}}', sdk_version)
        output_html = output_html.replace('{{YEAR}}', str(datetime.now().year))
        
        # Generate parameter documentation if needed
        param_html = ""
        for param in member_info['parameters']:
            param_html += f'<dt>{html.escape(param["name"])}</dt>'
            param_html += f'<dd>{html.escape(param["description"])}</dd>'
            
        output_html = output_html.replace('{{PARAMETERS}}', param_html)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        logger.info(f"Generated {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating member HTML: {str(e)}")

def generate_namespace_html(namespace, types, template_path, output_path, sdk_version):
    """
    Generate an HTML file for a namespace.
    
    Args:
        namespace: Namespace name
        types: List of types in the namespace
        template_path: Path to the HTML template file
        output_path: Path to write the output HTML
        sdk_version: SDK version string
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        output_html = template
        output_html = output_html.replace('{{NAMESPACE}}', namespace)
        output_html = output_html.replace('{{VERSION}}', sdk_version)
        output_html = output_html.replace('{{YEAR}}', str(datetime.now().year))
        
        # Generate list of types
        types_html = "<ul>"
        for type_info in types:
            types_html += f'<li><a href="T_{namespace}_{type_info["name"]}.htm">{type_info["name"]}</a></li>'
        types_html += "</ul>"
        
        output_html = output_html.replace('{{TYPES}}', types_html)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        logger.info(f"Generated {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating namespace HTML: {str(e)}")

def generate_toc_html(namespaces, template_path, output_path, sdk_version):
    """
    Generate a table of contents HTML file.
    
    Args:
        namespaces: Dictionary mapping namespace names to lists of types
        template_path: Path to the HTML template file
        output_path: Path to write the output HTML
        sdk_version: SDK version string
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        output_html = template
        output_html = output_html.replace('{{VERSION}}', sdk_version)
        output_html = output_html.replace('{{YEAR}}', str(datetime.now().year))
        
        # Generate TOC structure
        toc_html = "<ul>"
        for namespace, types in namespaces.items():
            toc_html += f'<li><a href="N_{namespace.replace(".", "_")}.htm">{namespace}</a><ul>'
            
            for type_name in types:
                toc_html += f'<li><a href="T_{namespace.replace(".", "_")}_{type_name}.htm">{type_name}</a></li>'
                
            toc_html += "</ul></li>"
        toc_html += "</ul>"
        
        output_html = output_html.replace('{{TOC}}', toc_html)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
            
        logger.info(f"Generated {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating TOC HTML: {str(e)}")

def copy_static_assets(source_dir, target_dir):
    """
    Copy static assets (CSS, JS, images) from source to target directory.
    
    Args:
        source_dir: Directory containing source static files
        target_dir: Directory to copy static files to
    """
    try:
        # Create directories if they don't exist
        for dirname in ['styles', 'scripts', 'icons']:
            os.makedirs(os.path.join(target_dir, dirname), exist_ok=True)
        
        # Copy styles
        styles_source = os.path.join(source_dir, 'styles')
        styles_target = os.path.join(target_dir, 'styles')
        
        if os.path.exists(styles_source):
            for file in os.listdir(styles_source):
                if file.endswith('.css'):
                    source_file = os.path.join(styles_source, file)
                    target_file = os.path.join(styles_target, file)
                    with open(source_file, 'rb') as sf, open(target_file, 'wb') as tf:
                        tf.write(sf.read())
        
        # Copy scripts
        scripts_source = os.path.join(source_dir, 'scripts')
        scripts_target = os.path.join(target_dir, 'scripts')
        
        if os.path.exists(scripts_source):
            for file in os.listdir(scripts_source):
                if file.endswith('.js'):
                    source_file = os.path.join(scripts_source, file)
                    target_file = os.path.join(scripts_target, file)
                    with open(source_file, 'rb') as sf, open(target_file, 'wb') as tf:
                        tf.write(sf.read())
        
        # Copy icons
        icons_source = os.path.join(source_dir, 'icons')
        icons_target = os.path.join(target_dir, 'icons')
        
        if os.path.exists(icons_source):
            for file in os.listdir(icons_source):
                if file.endswith('.png') or file.endswith('.gif') or file.endswith('.ico'):
                    source_file = os.path.join(icons_source, file)
                    target_file = os.path.join(icons_target, file)
                    with open(source_file, 'rb') as sf, open(target_file, 'wb') as tf:
                        tf.write(sf.read())
                        
        logger.info(f"Copied static assets from {source_dir} to {target_dir}")
        
    except Exception as e:
        logger.error(f"Error copying static assets: {str(e)}")
