"""
Helper module for parsing and processing XML mdoc files.

This module provides functions to extract information from mdoc XML files.
"""

import os
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def extract_namespace_info(mdoc_path):
    """
    Extract namespace information from mdoc files.
    
    Args:
        mdoc_path: Path to the mdoc directory
        
    Returns:
        A dictionary mapping namespace names to lists of types
    """
    namespaces = {}
    
    try:
        # Process the index.xml file if it exists
        index_path = os.path.join(mdoc_path, 'index.xml')
        if os.path.exists(index_path):
            tree = ET.parse(index_path)
            root = tree.getroot()
            
            for namespace in root.findall('./Namespace'):
                namespace_name = namespace.get('Name')
                if namespace_name:
                    namespaces[namespace_name] = []
                    
                    for type_elem in namespace.findall('./Type'):
                        type_name = type_elem.get('Name')
                        if type_name:
                            namespaces[namespace_name].append(type_name)
        else:
            # If no index.xml, infer from directory structure
            for item in os.listdir(mdoc_path):
                item_path = os.path.join(mdoc_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    namespace_name = item.replace('/', '.')
                    namespaces[namespace_name] = []
                    
                    for file in os.listdir(item_path):
                        if file.endswith('.xml'):
                            type_name = os.path.splitext(file)[0]
                            namespaces[namespace_name].append(type_name)
    
    except Exception as e:
        logger.error(f"Error extracting namespace info: {str(e)}")
    
    return namespaces

def extract_type_info(xml_file_path):
    """
    Extract type information from an mdoc XML file.
    
    Args:
        xml_file_path: Path to the XML file
        
    Returns:
        A dictionary with type information
    """
    type_info = {
        'name': '',
        'full_name': '',
        'kind': '',
        'namespace': '',
        'summary': '',
        'remarks': '',
        'members': []
    }
    
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        type_info['name'] = root.get('Name', '')
        type_info['full_name'] = root.get('FullName', '')
        
        # Determine kind (class, interface, enum, struct)
        if 'Interface' in type_info['name']:
            type_info['kind'] = 'interface'
        elif root.find('./EnumMembers') is not None:
            type_info['kind'] = 'enum'
        elif root.find('./Struct') is not None:
            type_info['kind'] = 'struct'
        else:
            type_info['kind'] = 'class'
        
        # Extract namespace
        if '.' in type_info['full_name']:
            type_info['namespace'] = '.'.join(type_info['full_name'].split('.')[:-1])
        
        # Extract docs
        docs_elem = root.find('./Docs')
        if docs_elem is not None:
            summary_elem = docs_elem.find('./summary')
            if summary_elem is not None and summary_elem.text:
                type_info['summary'] = summary_elem.text.strip()
            
            remarks_elem = docs_elem.find('./remarks')
            if remarks_elem is not None and remarks_elem.text:
                type_info['remarks'] = remarks_elem.text.strip()
        
        # Extract members
        for member in root.findall('./Members/Member'):
            member_info = {
                'name': member.get('MemberName', ''),
                'type': member.get('MemberType', ''),
                'summary': '',
                'remarks': '',
                'parameters': []
            }
            
            member_docs = member.find('./Docs')
            if member_docs is not None:
                summary_elem = member_docs.find('./summary')
                if summary_elem is not None and summary_elem.text:
                    member_info['summary'] = summary_elem.text.strip()
                
                remarks_elem = member_docs.find('./remarks')
                if remarks_elem is not None and remarks_elem.text:
                    member_info['remarks'] = remarks_elem.text.strip()
                
                # Extract parameters
                for param in member_docs.findall('./param'):
                    param_info = {
                        'name': param.get('name', ''),
                        'description': param.text.strip() if param.text else ''
                    }
                    member_info['parameters'].append(param_info)
            
            type_info['members'].append(member_info)
    
    except Exception as e:
        logger.error(f"Error extracting type info from {xml_file_path}: {str(e)}")
    
    return type_info

def map_csharp_to_java_type(csharp_type):
    """
    Map a C# type name to its Java equivalent for documentation lookup.
    
    Args:
        csharp_type: C# type name
        
    Returns:
        Java equivalent type name
    """
    # Common mappings
    mapping = {
        'System.String': 'java.lang.String',
        'System.Int32': 'int',
        'System.Boolean': 'boolean',
        'System.Void': 'void',
        'System.Object': 'java.lang.Object',
        # Add more mappings as needed
    }
    
    return mapping.get(csharp_type, csharp_type)
