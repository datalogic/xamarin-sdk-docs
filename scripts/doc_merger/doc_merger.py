#!/usr/bin/env python3
"""
Documentation merger for Datalogic Xamarin SDK.

This script merges documentation from two sources:
1. mdoc files (XML) containing the Xamarin documentation structure
2. javadoc files (HTML) containing the Java documentation comments

The merged result is used to create HTML files in the same format as the existing docs.
"""

import os
import sys
import argparse
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil
import logging
import html
import re

# Import our template helper
from template_helper import get_template

# Try to import BeautifulSoup, exit with error if not available
try:
    from bs4 import BeautifulSoup
    # Try with default parser first
    PARSER = "html.parser"  # Default parser that comes with Python
except ImportError:
    print("Error: beautifulsoup4 is not installed. Please install it using:")
    print("pip install beautifulsoup4")
    sys.exit(1)

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

class DocMerger:
    def __init__(self, mdoc_path, javadoc_path, html_template_path, output_path, version):
        self.mdoc_path = mdoc_path
        self.javadoc_path = javadoc_path
        self.html_template_path = html_template_path
        self.output_path = output_path
        self.version = version
        
        # Map to store the javadoc content indexed by class name
        self.javadoc_content = {}
        
        # Map to store namespace information: namespace -> {classes: [], interfaces: []}
        self.namespaces = {}
        
        # Count for statistics
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
    
    def replace_template_placeholders(self, soup, placeholder_values):
        """
        Replace all placeholders in the template with actual values.
        
        Args:
            soup: BeautifulSoup object of the template
            placeholder_values: Dictionary mapping placeholder names to values
        """
        
        html_str = str(soup)
        
        # Replace all placeholders in the HTML string
        for placeholder, value in placeholder_values.items():
            old_placeholder = '{{' + placeholder + '}}'
            
            if old_placeholder in html_str:
                html_str = html_str.replace(old_placeholder, str(value))
            else:
                if placeholder in ['SUMMARY', 'REMARKS']:
                    logger.info(f"Warning: Placeholder {{{placeholder}}} not found in template")
        
        # Handle complex placeholders that need special processing
        
        # Generate members sections (simplified for now)
        members_sections = self.generate_members_sections(placeholder_values.get('TYPE_NAME'))
        html_str = html_str.replace('{{MEMBERS_SECTIONS}}', members_sections)
        
        # Generate inheritance hierarchy (simplified for now)
        inheritance = self.generate_inheritance_hierarchy(placeholder_values.get('FULL_NAME'))
        html_str = html_str.replace('{{INHERITANCE}}', inheritance)
        
        # Generate syntax section (simplified for now)
        syntax = self.generate_syntax_section(placeholder_values.get('FULL_NAME'))
        html_str = html_str.replace('{{SYNTAX}}', syntax)
        
        # Generate see also section (simplified for now)
        see_also = self.generate_see_also_section(placeholder_values.get('NAMESPACE'))
        html_str = html_str.replace('{{SEE_ALSO}}', see_also)
        
        # Parse the updated HTML back into BeautifulSoup
        updated_soup = BeautifulSoup(html_str, PARSER)
        
        # Replace the original soup's contents
        soup.clear()
        soup.append(updated_soup)
        
    def generate_navigation_toc(self, namespace, type_name):
        """Generate navigation table of contents HTML."""
        # Templates now handle navigation content directly - no need for complex generation
        return ""
    
    def generate_members_sections(self, type_name):
        """Generate members sections HTML."""
        # Simplified implementation
        return f'''
        <div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID3RB')" onkeypress="SectionExpandCollapse_CheckKey('ID3RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID3RBToggle" src="../icons/SectionExpanded.png" />Constructors
          </span>
        </div>
        <div class="collapsibleSection" id="ID3RBSection">
          <p>Constructors will be populated dynamically based on class data.</p>
        </div>
        
        <div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID4RB')" onkeypress="SectionExpandCollapse_CheckKey('ID4RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID4RBToggle" src="../icons/SectionExpanded.png" />Properties
          </span>
        </div>
        <div class="collapsibleSection" id="ID4RBSection">
          <p>Properties will be populated dynamically based on class data.</p>
        </div>
        
        <div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID5RB')" onkeypress="SectionExpandCollapse_CheckKey('ID5RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID5RBToggle" src="../icons/SectionExpanded.png" />Methods
          </span>
        </div>
        <div class="collapsibleSection" id="ID5RBSection">
          <p>Methods will be populated dynamically based on class data.</p>
        </div>
        
        <div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID6RB')" onkeypress="SectionExpandCollapse_CheckKey('ID6RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID6RBToggle" src="../icons/SectionExpanded.png" />Fields
          </span>
        </div>
        <div class="collapsibleSection" id="ID6RBSection">
          <p>Fields will be populated dynamically based on class data.</p>
        </div>
        '''
    
    def generate_inheritance_hierarchy(self, full_name):
        """Generate inheritance hierarchy HTML."""
        return f'''
        <div class="inheritance">
          <div>System.Object</div>
          <div style="margin-left: 15px;">{full_name}</div>
        </div>
        '''
    
    def generate_syntax_section(self, full_name):
        """Generate syntax section HTML."""
        return f'''
        <div class="codeSnippetContainer">
          <div class="codeSnippetContainerTabs">
            <div class="codeSnippetContainerTab">
              <a href="#" onclick="javascript:ChangeTab('syntax','cs','1','2');return false;">C#</a>
            </div>
          </div>
          <div class="codeSnippetContainerCodeContainer">
            <div class="codeSnippetContainerCode">
              <pre xml:space="preserve"><span class="keyword">public class</span> <span class="identifier">{full_name.split('.')[-1]}</span></pre>
            </div>
          </div>
        </div>
        '''
    
    def generate_see_also_section(self, namespace):
        """Generate see also section HTML."""
        return f'''
        <a href="N_{namespace.replace('.', '_')}.htm">{namespace} Namespace</a>
        '''
        
    def load_javadoc_content(self):
        """Load all javadoc HTML files and extract their content."""
        logger.info(f"Loading JavaDoc content from: {self.javadoc_path}")
        
        # Walk through the javadoc directory
        for root, _, files in os.walk(self.javadoc_path):
            for file in files:
                if file.endswith('.html') and not file.endswith('package-summary.html'):
                    try:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.javadoc_path)
                        
                        # Get class name from file path
                        class_path = os.path.splitext(relative_path)[0]
                        # Handle both Windows (\) and Unix (/) path separators
                        class_name = class_path.replace('\\', '.').replace('/', '.')
                        
                        # Load and parse HTML
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        soup = BeautifulSoup(content, PARSER)
                        
                        # Mark all javadoc href links with special prefix
                        self._mark_javadoc_hrefs(soup)
                        
                        # Store the soup object for later use
                        self.javadoc_content[class_name] = soup
                        
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {str(e)}")
        
        logger.info(f"Loaded {len(self.javadoc_content)} JavaDoc files")
    
    def _mark_javadoc_hrefs(self, soup):
        """Mark all href links in javadoc content with special prefix for later fixing."""
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Mark relative links that point to HTML files or are fragment-only references
            if (href and 
                not href.startswith('http') and 
                not href.startswith('mailto:') and
                (href.endswith('.html') or href.startswith('#'))):
                # Add special prefix to mark this as a javadoc link that needs fixing
                link['href'] = f"JAVADOC_LINK_FIX:{href}"
    
    def _convert_javadoc_href_to_xamarin_format(self, javadoc_href):
        """Convert javadoc href format to xamarin documentation format.
        
        Examples:
            StopListener.html -> files ending with StopListener.htm
            DecodeException.html#SUCCESS -> F_Com_Datalogic_Decode_DecodeException_Success.htm
            #removeInitListener(com.datalogic.decode.InitListener) -> removeInitListener
            PropertyID.html#SEND_CODE_ID -> F_Com_Datalogic_Decode_PropertyID_SendCodeId.htm
            
        Args:
            javadoc_href: The original javadoc href (e.g., "StopListener.html" or "DecodeException.html#SUCCESS")
            
        Returns:
            str: The converted xamarin format filename pattern to search for
        """
        if not javadoc_href:
            return None
        
        # Handle fragment-only hrefs (starting with #)
        if javadoc_href.startswith('#'):
            # Remove the # and extract method name before parentheses
            fragment = javadoc_href[1:]
            # Split on '(' to get just the method name part
            method_name = fragment.split('(')[0]
            return method_name
            
        # Remove .html extension
        href_without_ext = javadoc_href.replace('.html', '')
        
        if '#' in href_without_ext:
            # Handle anchor links like "DecodeException.html#SUCCESS" or 
            # "PropertyID.html#SEND_CODE_ID"
            class_part, anchor_part = href_without_ext.split('#', 1)
            
            # Split on '(' to get just the name part before any parameters
            anchor_name = anchor_part.split('(')[0]
            
            # Check if anchor_name is in ALL_CAPS_WITH_UNDERSCORES format
            # and convert it to PascalCase for better matching
            if '_' in anchor_name and anchor_name.isupper():
                # Convert SEND_CODE_ID to SendCodeId
                words = anchor_name.split('_')
                anchor_name = ''.join(word.capitalize() for word in words)
            
            # Convert to format: ClassName_AnchorName.htm
            # The actual file might be F_Com_Datalogic_Decode_ClassName_AnchorName.htm
            return f"{class_part}_{anchor_name}.htm"
        else:
            # Handle simple class references like "StopListener.html"
            # The actual file might be T_Com_Datalogic_Decode_IStopListener.htm or similar
            return f"{href_without_ext}.htm"
    
    def _find_matching_xamarin_file(self, search_pattern, output_path):
        """Find the actual xamarin documentation file that matches the search pattern.
        
        Prioritizes files with underscore pattern (types/interfaces) over method files.
        
        Args:
            search_pattern: The pattern to search for (e.g., "DeinitListener", "removeInitListener")
            output_path: The path to search in for matching files
            
        Returns:
            str: The actual filename if found, or None if not found
        """
        if not search_pattern or not output_path:
            return None
            
        try:
            # Get all .htm files in the output directory
            html_files = []
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    if file.endswith('.htm'):
                        html_files.append(file)
            
            if not html_files:
                logger.warning(f"No .htm files found in {output_path}")
                return None
            
            # Remove .htm extension from search pattern if present
            base_pattern = search_pattern.replace('.htm', '')
            
            # Priority 1: Look for files with underscore pattern "_SearchPattern.htm"
            # This should match types/interfaces like T_Com_Datalogic_Decode_IDeinitListener.htm
            priority_matches = []
            for filename in html_files:
                if f"_{base_pattern}.htm" in filename:
                    priority_matches.append(filename)
            
            if priority_matches:
                # Sort to get the most likely match (shortest name often best)
                priority_matches.sort(key=len)
                logger.debug(f"Found priority match for '{search_pattern}': {priority_matches[0]}")
                return priority_matches[0]
            
            # Priority 2: Look for files ending with the search pattern
            # This catches method files like M_Com_Datalogic_Decode_BarcodeManager_AddDeinitListener.htm
            fallback_matches = []
            for filename in html_files:
                if filename.endswith(f"{base_pattern}.htm"):
                    fallback_matches.append(filename)
            
            if fallback_matches:
                # Sort to get the most likely match
                fallback_matches.sort(key=len)
                logger.debug(f"Found fallback match for '{search_pattern}': {fallback_matches[0]}")
                return fallback_matches[0]
            
            # Priority 3: Look for files containing the search pattern anywhere
            contains_matches = []
            for filename in html_files:
                if base_pattern.lower() in filename.lower():
                    contains_matches.append(filename)
            
            if contains_matches:
                # Sort to get the most likely match
                contains_matches.sort(key=len)
                logger.debug(f"Found contains match for '{search_pattern}': {contains_matches[0]}")
                return contains_matches[0]
            
            # logger.debug(f"No matching file found for search pattern: {search_pattern}")
            return None
                        
        except Exception as e:
            logger.error(f"Error searching for file matching {search_pattern}: {str(e)}")
            return None
    
    def fix_javadoc_links_in_files(self):
        """Process all generated HTML files and fix javadoc links marked with JAVADOC_LINK_FIX prefix."""
        logger.info("Fixing javadoc links in generated HTML files...")
        
        if not os.path.exists(self.output_path):
            logger.warning(f"Output path does not exist: {self.output_path}")
            return
            
        fixed_count = 0
        total_files = 0
        
        # Process all HTML files in the output directory
        for root, _, files in os.walk(self.output_path):
            for file in files:
                if file.endswith('.htm'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    try:
                        # Read the file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check if the file contains any javadoc links to fix
                        if 'JAVADOC_LINK_FIX:' not in content:
                            continue
                            
                        # Parse with BeautifulSoup
                        soup = BeautifulSoup(content, PARSER)
                        
                        # Find and fix all javadoc links
                        links_fixed = 0
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('JAVADOC_LINK_FIX:'):
                                # Extract the original javadoc href
                                original_href = href.replace('JAVADOC_LINK_FIX:', '')
                                
                                # Convert to xamarin format
                                search_pattern = self._convert_javadoc_href_to_xamarin_format(original_href)
                                
                                if search_pattern:
                                    # Handle different cases
                                    if original_href.startswith('#'):
                                        # Fragment-only reference - search for method name
                                        method_name = search_pattern  # This is just the method name now
                                        matching_file = self._find_matching_xamarin_file(method_name, self.output_path)
                                    elif '#' in original_href:
                                        # File with fragment - try the combined pattern first, then just the base file
                                        matching_file = self._find_matching_xamarin_file(search_pattern, self.output_path)
                                        if not matching_file:
                                            # Try just the base filename
                                            base_pattern = search_pattern.split('_')[0] if '_' in search_pattern else search_pattern.replace('.htm', '')
                                            matching_file = self._find_matching_xamarin_file(base_pattern, self.output_path)
                                    else:
                                        # Simple file reference
                                        base_name = search_pattern.replace('.htm', '')
                                        matching_file = self._find_matching_xamarin_file(base_name, self.output_path)
                                    
                                    if matching_file:
                                        # Update the href to point to the correct file
                                        link['href'] = f"../html/{matching_file}"
                                        links_fixed += 1
                                        logger.debug(f"Fixed link: {original_href} -> {matching_file}")
                                    else:
                                        # If no matching file found, remove the prefix but keep the original link
                                        # This will result in a broken link, but it's better than the prefix
                                        link['href'] = original_href
                                        # logger.warning(f"No matching file found for javadoc link: {original_href}")
                        
                        # Only write back if we made changes
                        if links_fixed > 0:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(str(soup))
                            fixed_count += links_fixed
                            logger.debug(f"Fixed {links_fixed} links in {file}")
                            
                    except Exception as e:
                        logger.error(f"Error fixing links in {file_path}: {str(e)}")
        
        logger.info(f"Link fixing complete. Fixed {fixed_count} links across {total_files} files.")
    
    def extract_javadoc_description(self, class_name, child_name=None):
        """Extract description from the javadoc files.
        
        This method maintains backward compatibility while using the new JavaDocExtractor.
        
        Args:
            class_name: The full class name
            child_name: Optional member name (property, method, field)
            
        Returns:
            tuple: (summary, remarks) extracted from JavaDoc
        """
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            if not child_name:
                # Class documentation
                return self._javadoc_extractor.extract_class_documentation(class_name)
            else:
                # Member documentation - use full documentation for backward compatibility
                return self._javadoc_extractor.extract_member_full_documentation(class_name, child_name)
                
        except Exception as e:
            logger.error(f"Error extracting javadoc for {class_name}.{child_name}: {str(e)}")
            return ("", "")
    
    def extract_javadoc_for_table(self, class_name, member_name):
        """Extract brief summary for member tables.
        
        Args:
            class_name: The full class name
            member_name: The member name
            
        Returns:
            str: Brief summary suitable for table display
        """
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            return self._javadoc_extractor.extract_member_table_summary(class_name, member_name)
        except Exception as e:
            logger.error(f"Error extracting table summary for {class_name}.{member_name}: {str(e)}")
            return ""
    
    def extract_javadoc_method_details(self, class_name, method_name):
        """Extract complete method documentation including parameters, return value, and exceptions.
        
        Args:
            class_name: The full class name
            method_name: The method name
            
        Returns:
            dict: Dictionary containing 'summary', 'remarks', 'parameters', 'return_value', 'exceptions'
        """
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            summary, remarks = self._javadoc_extractor.extract_member_full_documentation(class_name, method_name)
            parameters = self._javadoc_extractor.extract_method_parameters(class_name, method_name)
            return_value = self._javadoc_extractor.extract_method_return_value(class_name, method_name)
            exceptions = self._javadoc_extractor.extract_method_exceptions(class_name, method_name)
            
            return {
                'summary': summary,
                'remarks': remarks,
                'parameters': parameters,
                'return_value': return_value,
                'exceptions': exceptions
            }
        except Exception as e:
            logger.error(f"Error extracting method details for {class_name}.{method_name}: {str(e)}")
            return {
                'summary': "",
                'remarks': "",
                'parameters': [],
                'return_value': "",
                'exceptions': []
            }
    
    def extract_javadoc_parameters(self, class_name, member_name):
        """Extract parameter documentation from JavaDoc <dl class="notes"> section."""
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            return self._javadoc_extractor.extract_method_parameters(class_name, member_name)
        except Exception as e:
            logger.error(f"Error extracting parameters for {class_name}.{member_name}: {str(e)}")
            return []
    
    def extract_javadoc_return_value(self, class_name, member_name):
        """Extract return value documentation from JavaDoc <dl class="notes"> section."""
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            return self._javadoc_extractor.extract_method_return_value(class_name, member_name)
        except Exception as e:
            logger.error(f"Error extracting return value for {class_name}.{member_name}: {str(e)}")
            return ""
    
    def extract_javadoc_exceptions(self, class_name, member_name):
        """Extract exceptions documentation from JavaDoc <dl class="notes"> section."""
        if not hasattr(self, '_javadoc_extractor'):
            self._javadoc_extractor = self.JavaDocExtractor(self.javadoc_content)
        
        try:
            return self._javadoc_extractor.extract_method_exceptions(class_name, member_name)
        except Exception as e:
            logger.error(f"Error extracting exceptions for {class_name}.{member_name}: {str(e)}")
            return []

    def extract_namespace_info(self):
        """Extract namespace information from index.xml file."""
        logger.info("Extracting namespace information from index.xml...")
        
        index_file = os.path.join(self.mdoc_path, 'index.xml')
        if not os.path.exists(index_file):
            logger.warning(f"index.xml not found at {index_file}")
            return
        
        try:
            tree = ET.parse(index_file)
            root = tree.getroot()
            
            # Find all namespace elements
            for namespace_elem in root.findall('.//Namespace'):
                namespace_name = namespace_elem.get('Name')
                if not namespace_name:
                    continue
                
                if namespace_name not in self.namespaces:
                    self.namespaces[namespace_name] = {
                        'classes': [],
                        'interfaces': [],
                        'enums': []
                    }
                
                # Find all types in this namespace
                for type_elem in namespace_elem.findall('Type'):
                    type_name = type_elem.get('Name')
                    type_kind = type_elem.get('Kind')
                    
                    if not type_name or not type_kind:
                        continue
                    
                    # Categorize the type
                    if type_kind == 'Class':
                        self.namespaces[namespace_name]['classes'].append(type_name)
                    elif type_kind == 'Interface':
                        self.namespaces[namespace_name]['interfaces'].append(type_name)
                    elif type_kind == 'Enum':
                        self.namespaces[namespace_name]['enums'].append(type_name)
            
            logger.info(f"Extracted information for {len(self.namespaces)} namespaces")
            
        except Exception as e:
            logger.error(f"Error extracting namespace info: {str(e)}")
    
    def process_mdoc_files(self):
        """Process all mdoc XML files and generate HTML documentation."""
        logger.info("Processing mdoc files...")
        
        # First, extract namespace information from index.xml
        self.extract_namespace_info()
        
        # Walk through the mdoc directory
        for root, _, files in os.walk(self.mdoc_path):
            for file in files:
                if file.endswith('.xml') and file != 'index.xml':
                    try:
                        file_path = os.path.join(root, file)
                        self.process_mdoc_file(file_path)
                        self.processed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        self.error_count += 1
        
        logger.info(f"Processed {self.processed_count} files: {self.success_count} successful, {self.error_count} errors")
        
        # Generate namespace pages
        self.generate_namespace_pages()
        
        # After all files are generated, fix the javadoc links
        self.fix_javadoc_links_in_files()
    
    def process_mdoc_file(self, file_path):
        """Process a single mdoc XML file."""
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Get the full name
            full_name = root.get('FullName')
            
            # Extract class documentation from javadoc (use full_name directly as it's already in dot format)
            class_summary, class_remarks = self.extract_javadoc_description(full_name)
            
            # Update the XML with the javadoc documentation
            docs_element = root.find('./Docs')
            if docs_element is not None:
                summary_element = docs_element.find('./summary')
                if summary_element is not None and (summary_element.text is None or summary_element.text.strip() == "To be added."):
                    # For XML, we need to extract plain text from HTML
                    if class_summary:
                        # Parse HTML and extract text content
                        from bs4 import BeautifulSoup
                        soup_temp = BeautifulSoup(class_summary, 'html.parser')
                        summary_element.text = soup_temp.get_text(' ', strip=True)
                    else:
                        summary_element.text = "To be added."
                
                remarks_element = docs_element.find('./remarks')
                if remarks_element is not None and (remarks_element.text is None or remarks_element.text.strip() == "To be added."):
                    if class_remarks:
                        # For XML, we need to extract plain text from HTML
                        from bs4 import BeautifulSoup
                        soup_temp = BeautifulSoup(class_remarks, 'html.parser')
                        remarks_element.text = soup_temp.get_text(' ', strip=True)
                        # Add link to Android documentation if available
                        # Convert to path format for URL
                        class_path = full_name.replace('Com.', 'com/').replace('.', '/')
                        remarks_element.text += f"\n\n[Android Documentation](http://datalogic.github.io/android-sdk-docs/reference/{class_path}.html)"
            
            # Process members
            for member in root.findall('./Members/Member'):
                member_name = member.get('MemberName')
                
                # Extract member documentation from javadoc
                member_summary, member_remarks = self.extract_javadoc_description(full_name, member_name)
                
                # Update the member docs
                member_docs = member.find('./Docs')
                if member_docs is not None:
                    member_summary_elem = member_docs.find('./summary')
                    if member_summary_elem is not None and (member_summary_elem.text is None or member_summary_elem.text.strip() == "To be added."):
                        member_summary_elem.text = member_summary if member_summary else "To be added."
                    
                    member_remarks_elem = member_docs.find('./remarks')
                    if member_remarks_elem is not None and (member_remarks_elem.text is None or member_remarks_elem.text.strip() == "To be added."):
                        if member_remarks:
                            member_remarks_elem.text = member_remarks
            
            # Generate HTML from the updated XML
            self.generate_html_from_xml(root, file_path)
            
            # Generate component files (properties, methods, individual pages)
            self.generate_component_files(root)
            
            logger.info(f"Class: {full_name}")
            logger.info(f"  Extracted javadoc summary: {class_summary[:100] if class_summary else 'None'}")
            logger.info(f"  Extracted javadoc remarks: {class_remarks[:100] if class_remarks else 'None'}")
            
            # Update XML logging
            if docs_element is not None:
                summary_element = docs_element.find('./summary')
                if summary_element is not None:
                    logger.info(f"  Updated XML summary: {summary_element.text[:100] if summary_element.text else 'None'}")
                
                remarks_element = docs_element.find('./remarks')
                if remarks_element is not None:
                    logger.info(f"  Updated XML remarks: {remarks_element.text[:100] if remarks_element.text else 'None'}")
            
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"Error in process_mdoc_file for {file_path}: {str(e)}")
            raise
    
    def generate_html_from_xml(self, xml_root, xml_file_path):
        """Generate an HTML file from the XML documentation."""
        try:
            type_name = xml_root.get('Name')
            full_name = xml_root.get('FullName')
            
            # Determine the output file path
            relative_path = os.path.relpath(xml_file_path, self.mdoc_path)
            namespace_path = os.path.dirname(relative_path)
            
            # Create full name with underscores for filenames
            full_name_underscored = full_name.replace('.', '_')
            
            # Create output filename
            html_filename = f"T_{full_name_underscored}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Read the HTML template using template helper
            soup = get_template('class', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load class template from {self.html_template_path}")
                return
            
            # Extract documentation content
            docs_elem = xml_root.find('./Docs')
            summary = ""
            remarks = ""
            
            # Extract JavaDoc content directly for HTML (preserving rich formatting)
            javadoc_summary, javadoc_remarks = self.extract_javadoc_description(full_name)
            
            if docs_elem is not None:
                summary_elem = docs_elem.find('./summary')
                if summary_elem is not None and summary_elem.text:
                    summary = summary_elem.text.strip()
                
                remarks_elem = docs_elem.find('./remarks')
                if remarks_elem is not None and remarks_elem.text:
                    remarks = remarks_elem.text.strip()
            
            # Use JavaDoc content
            if javadoc_summary:
                summary = javadoc_summary
            if javadoc_remarks:
                remarks = javadoc_remarks
            
            # Extract namespace from full name
            namespace = '.'.join(full_name.split('.')[:-1])
            
            # Update template with actual values
            self.replace_template_placeholders(soup, {
                'TYPE_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'SUMMARY': summary if summary else "To be added.",
                'FILE_NAME': f"T_{full_name_underscored}",
                'NAMESPACE_LINK': f"N_{namespace.replace('.', '_')}.htm",
                'ASSEMBLY_INFO': "datalogic-xamarin-sdk (in datalogic-xamarin-sdk.dll) Version: 1.0.0.0 (1.0.0.0)"
            })
            
            # Update TOC navigation
            # Update namespace links (toclevel0)
            namespace_divs = soup.select('div.toclevel0[data-toclevel="0"]')
            for div in namespace_divs:
                links = div.select('a[data-tochassubtree="true"]')
                for link in links:
                    # Check if it's a namespace entry with the wrong namespace
                    if 'tocid' in link.attrs and link['tocid'].startswith('N_') and 'Cradle' in link.get('title', ''):
                        # Replace it with the correct namespace
                        link['href'] = f"../html/N_{namespace.replace('.', '_')}.htm"
                        link['title'] = namespace
                        link['tocid'] = f"N_{namespace.replace('.', '_')}"
                        link.string = namespace
            
            # Update class links (toclevel1)
            class_divs = soup.select('div.toclevel1[data-toclevel="1"]')
            for div in class_divs:
                if 'current' in div.get('class', []):
                    type_links = div.select('a[data-tochassubtree="true"]')
                    for link in type_links:
                        link['href'] = f"../html/T_{full_name.replace('.', '_')}.htm"
                        link['title'] = f"{type_name} Class"
                        link['tocid'] = f"T_{full_name.replace('.', '_')}"
                        link.string = f"{type_name} Class"
            
            # Extract members from XML to determine what sections to show
            has_constructors = False
            has_properties = False
            has_methods = False
            has_fields = False
            
            for member in xml_root.findall('./Members/Member'):
                member_type_elem = member.find('./MemberType')
                member_type = member_type_elem.text if member_type_elem is not None else None
                
                if member_type == 'Constructor':
                    has_constructors = True
                elif member_type == 'Property':
                    has_properties = True
                elif member_type == 'Method':
                    has_methods = True
                elif member_type == 'Field':
                    has_fields = True
            
            # Update member links (toclevel2) and remove sections that have no members
            member_divs = soup.select('div.toclevel2[data-toclevel="2"]')
            divs_to_remove = []
            
            for div in member_divs:
                member_links = div.select('a')
                for link in member_links:
                    link_title = link.get('title', '')
                    # Use more specific matching to avoid false positives
                    # Check if the title ends with the section name (e.g., "Properties", "Methods", etc.)
                    if link_title.endswith(' Constructor') or link_title.endswith(' Constructor '):
                        if has_constructors:
                            link['href'] = f"../html/M_{full_name.replace('.', '_')}__ctor.htm"
                            link['title'] = f"{type_name} Constructor "
                            link['tocid'] = f"M_{full_name.replace('.', '_')}__ctor"
                            link.string = f"{type_name} Constructor\n            "
                        else:
                            divs_to_remove.append(div)
                    elif link_title.endswith(' Properties'):
                        if has_properties:
                            link['href'] = f"../html/Properties_T_{full_name.replace('.', '_')}.htm"
                            link['title'] = f"{type_name} Properties"
                            link['tocid'] = f"Properties_T_{full_name.replace('.', '_')}"
                            link.string = f"{type_name} Properties"
                        else:
                            divs_to_remove.append(div)
                    elif link_title.endswith(' Methods'):
                        if has_methods:
                            link['href'] = f"../html/Methods_T_{full_name.replace('.', '_')}.htm"
                            link['title'] = f"{type_name} Methods"
                            link['tocid'] = f"Methods_T_{full_name.replace('.', '_')}"
                            link.string = f"{type_name} Methods"
                        else:
                            divs_to_remove.append(div)
                    elif link_title.endswith(' Fields'):
                        if has_fields:
                            link['href'] = f"../html/Fields_T_{full_name.replace('.', '_')}.htm"
                            link['title'] = f"{type_name} Fields"
                            link['tocid'] = f"Fields_T_{full_name.replace('.', '_')}"
                            link.string = f"{type_name} Fields"
                        else:
                            divs_to_remove.append(div)
            
            # Remove sidebar entries for empty sections
            for div in divs_to_remove:
                div.decompose()
            
            # Update summary
            summary_div = soup.select_one('div.summary')
            if summary_div:
                summary_div.clear()
                if summary and summary != "To be added.":
                    # If summary contains HTML, parse it and insert as HTML
                    if '<' in summary and '>' in summary:
                        summary_soup = BeautifulSoup(summary, PARSER)
                        # Insert all contents of the parsed HTML
                        for element in summary_soup.children:
                            if hasattr(element, 'name'):  # It's a tag
                                summary_div.append(element)
                            else:  # It's text
                                summary_div.append(soup.new_string(str(element)))
                    else:
                        summary_div.append(soup.new_string(summary))
                else:
                    summary_div.append(soup.new_string("To be added."))
            
            # Update inheritance hierarchy
            inheritance_section = soup.select_one('div#ID0RBSection')
            if inheritance_section and '{{INHERITANCE}}' in inheritance_section.text:
                inheritance_section.clear()
                base_type = xml_root.get('BaseType') or 'Object'
                inheritance_html = f'<span class="nolink">Object</span><br />  <span class="selflink">{full_name}</span><br />'
                inheritance_section.append(BeautifulSoup(inheritance_html, PARSER))
            
            # Update syntax section
            syntax_section = soup.select_one('div#ID2RBSection')
            if syntax_section:
                syntax_section.clear()
                
                # Extract base class and interfaces from XML
                base_element = xml_root.find('.//Base/BaseTypeName')
                base_class = base_element.text if base_element is not None else 'Object'
                base_class_short = base_class.split('.')[-1]  # Get short name like "Object"
                
                interfaces = []
                # Define preferred order to match original HTML files
                interface_order = [
                    'IPropertyEditor', 'IPropertyGetter', 'IJavaObject', 'IDisposable', 'IJavaPeerable'
                ]
                
                interface_elements = xml_root.findall('.//Interfaces/Interface/InterfaceName')
                found_interfaces = {}
                for interface_elem in interface_elements:
                    interface_name = interface_elem.text
                    interface_short = interface_name.split('.')[-1]
                    found_interfaces[interface_short] = True
                
                # Add interfaces in preferred order
                for interface_name in interface_order:
                    if interface_name in found_interfaces:
                        interfaces.append(interface_name)
                
                # Build C# syntax
                cs_syntax = f'<span class="keyword">public</span> <span class="keyword">class</span> <span class="identifier">{type_name}</span>'
                if base_class_short != 'Object':
                    cs_syntax += f' : <span class="identifier">{base_class_short}</span>'
                    if interfaces:
                        cs_syntax += f', \n\t' + ', '.join([f'<span class="identifier">{iface}</span>' for iface in interfaces])
                elif interfaces:
                    cs_syntax += f' : <span class="identifier">{base_class_short}</span>, \n\t' + ', '.join([f'<span class="identifier">{iface}</span>' for iface in interfaces])
                
                # Build VB.NET syntax
                vb_syntax = f'<span class="keyword">Public</span> <span class="keyword">Class</span> <span class="identifier">{type_name}</span>'
                if base_class_short != 'Object':
                    vb_syntax += f'\n\t<span class="keyword">Inherits</span> <span class="identifier">{base_class_short}</span>'
                if interfaces:
                    vb_syntax += f'\n\t<span class="keyword">Implements</span> ' + ', '.join([f'<span class="identifier">{iface}</span>' for iface in interfaces])
                
                syntax_html = f"""<div class="codeSnippetContainer"><div class="codeSnippetContainerTabs">
                <div id="ID1EBCA_tab1" class="codeSnippetContainerTab"><a href="#" onclick="javascript:ChangeTab('ID1EBCA','cs','1','2');return false;">C#</a></div>
                <div id="ID1EBCA_tab2" class="codeSnippetContainerTab"><a href="#" onclick="javascript:ChangeTab('ID1EBCA','vb','2','2');return false;">VB</a></div>
                </div><div class="codeSnippetContainerCodeContainer"><div class="codeSnippetToolBar"><div class="codeSnippetToolBarText">
                <a id="ID1EBCA_copyCode" href="#" class="copyCodeSnippet" onclick="javascript:CopyToClipboard('ID1EBCA');return false;" title="Copy">Copy</a></div></div>
                <div id="ID1EBCA_code_Div1" class="codeSnippetContainerCode" style="display: block">
                <pre xml:space="preserve">{cs_syntax}</pre></div>
                <div id="ID1EBCA_code_Div2" class="codeSnippetContainerCode" style="display: none">
                <pre xml:space="preserve">{vb_syntax}</pre></div>
                </div></div><script type="text/javascript">AddLanguageTabSet("ID1EBCA");</script>"""
                syntax_section.append(BeautifulSoup(syntax_html, PARSER))
            
            # Update namespace in breadcrumb navigation
            namespace_link = soup.select_one('div.pageBody strong:contains("Namespace:") + a')
            if namespace_link:
                namespace_link['href'] = f"N_{namespace.replace('.', '_')}.htm"
                namespace_link.string = namespace
            
            # Extract members from XML by type
            constructors = []
            properties = []
            methods = []
            fields = []
            
            for member in xml_root.findall('./Members/Member'):
                member_type_elem = member.find('./MemberType')
                member_type = member_type_elem.text if member_type_elem is not None else None
                member_name = member.get('MemberName')
                
                # Get documentation for this member
                member_docs = member.find('./Docs')
                member_summary = ""
                if member_docs is not None and member_docs.find('./summary') is not None:
                    member_summary = member_docs.find('./summary').text or ""
                
                # Create a dictionary with member information
                member_info = {
                    'name': member_name,
                    'summary': member_summary if member_summary else "To be added."
                }
                
                # Add to the appropriate list based on member type
                if member_type == 'Constructor':
                    # For constructors, use a standard .NET description
                    member_info['summary'] = f"Initializes a new instance of the {type_name} class"
                    constructors.append(member_info)
                elif member_type == 'Property':
                    properties.append(member_info)
                elif member_type == 'Method':
                    methods.append(member_info)
                elif member_type == 'Field':
                    fields.append(member_info)
            
            # Update constructors section
            constructors_section = soup.select_one('div#ID3RBSection')
            constructors_region = soup.select_one('div.collapsibleAreaRegion:has(span[onclick*="ID3RB"])')
            
            if len(constructors) > 0:
                if constructors_section:
                    constructors_section.clear()
                    constructors_table = BeautifulSoup('<table class="members" id="constructorList"><tr><th class="iconColumn"></th><th>Name</th><th>Description</th></tr></table>', PARSER).table
                    
                    for constructor in constructors:
                        tr = soup.new_tag('tr')
                        
                        # Icon column
                        td_icon = soup.new_tag('td')
                        td_icon.append(soup.new_tag('img', attrs={
                            'src': '../icons/pubmethod.gif',
                            'alt': 'Public method',
                            'title': 'Public method'
                        }))
                        tr.append(td_icon)
                        
                        # Name column
                        td_name = soup.new_tag('td')
                        a_tag = soup.new_tag('a', attrs={
                            'href': f"M_{full_name_underscored}__ctor.htm"
                        })
                        a_tag.string = f"{type_name}"
                        td_name.append(a_tag)
                        tr.append(td_name)
                        
                        # Description column
                        td_desc = soup.new_tag('td')
                        div_summary_html = f'''<div class="summary">{constructor['summary']}</div>'''
                        div_summary_parsed = BeautifulSoup(div_summary_html, PARSER)
                        td_desc.append(div_summary_parsed)
                        tr.append(td_desc)
                        
                        constructors_table.append(tr)
                    
                    constructors_section.append(constructors_table)
                    top_link = soup.new_tag('a', attrs={'href': '#PageHeader'})
                    top_link.string = 'Top'
                    constructors_section.append(top_link)
            else:
                # Remove both the region header and section content for empty constructors
                if constructors_region:
                    constructors_region.decompose()
                if constructors_section:
                    constructors_section.decompose()
            
            # Update properties section
            properties_section = soup.select_one('div#ID4RBSection')
            properties_region = soup.select_one('div.collapsibleAreaRegion:has(span[onclick*="ID4RB"])')
            
            if len(properties) > 0:
                if properties_section:
                    properties_section.clear()
                    properties_table = BeautifulSoup('<table class="members" id="propertyList"><tr><th class="iconColumn"></th><th>Name</th><th>Description</th></tr></table>', PARSER).table
                    
                    for prop in properties:
                        tr = soup.new_tag('tr')
                        
                        # Icon column
                        td_icon = soup.new_tag('td')
                        td_icon.append(soup.new_tag('img', attrs={
                            'src': '../icons/pubproperty.gif',
                            'alt': 'Public property',
                            'title': 'Public property'
                        }))
                        tr.append(td_icon)
                        
                        # Name column
                        td_name = soup.new_tag('td')
                        a_tag = soup.new_tag('a', attrs={
                            'href': f"P_{full_name_underscored}_{prop['name']}.htm"
                        })
                        a_tag.string = prop['name']
                        td_name.append(a_tag)
                        tr.append(td_name)
                        
                        # Description column
                        td_desc = soup.new_tag('td')
                        div_summary_html = f'''<div class="summary">{prop['summary']}</div>'''
                        div_summary_parsed = BeautifulSoup(div_summary_html, PARSER)
                        td_desc.append(div_summary_parsed)
                        tr.append(td_desc)
                        
                        properties_table.append(tr)
                    
                    properties_section.append(properties_table)
                    top_link = soup.new_tag('a', attrs={'href': '#PageHeader'})
                    top_link.string = 'Top'
                    properties_section.append(top_link)
            else:
                # Remove both the region header and section content for empty properties
                if properties_region:
                    properties_region.decompose()
                if properties_section:
                    properties_section.decompose()
            
            # Update methods section
            methods_section = soup.select_one('div#ID5RBSection')
            methods_region = soup.select_one('div.collapsibleAreaRegion:has(span[onclick*="ID5RB"])')
            
            if len(methods) > 0:
                if methods_section:
                    methods_section.clear()
                    methods_table = BeautifulSoup('<table class="members" id="methodList"><tr><th class="iconColumn"></th><th>Name</th><th>Description</th></tr></table>', PARSER).table
                    
                    for method in methods:
                        tr = soup.new_tag('tr')
                        
                        # Icon column
                        td_icon = soup.new_tag('td')
                        td_icon.append(soup.new_tag('img', attrs={
                            'src': '../icons/pubmethod.gif',
                            'alt': 'Public method',
                            'title': 'Public method'
                        }))
                        tr.append(td_icon)
                        
                        # Name column
                        td_name = soup.new_tag('td')
                        a_tag = soup.new_tag('a', attrs={
                            'href': f"M_{full_name_underscored}_{method['name']}.htm"
                        })
                        a_tag.string = method['name']
                        td_name.append(a_tag)
                        tr.append(td_name)
                        
                        # Description column
                        td_desc = soup.new_tag('td')
                        div_summary_html = f'''<div class="summary">{method['summary']}</div>'''
                        div_summary_parsed = BeautifulSoup(div_summary_html, PARSER)
                        td_desc.append(div_summary_parsed)
                        tr.append(td_desc)
                        
                        methods_table.append(tr)
                    
                    methods_section.append(methods_table)
                    top_link = soup.new_tag('a', attrs={'href': '#PageHeader'})
                    top_link.string = 'Top'
                    methods_section.append(top_link)
            else:
                # Remove both the region header and section content for empty methods
                if methods_region:
                    methods_region.decompose()
                if methods_section:
                    methods_section.decompose()
            
            # Update fields section
            fields_section = soup.select_one('div#ID6RBSection')
            fields_region = soup.select_one('div.collapsibleAreaRegion:has(span[onclick*="ID6RB"])')
            
            if len(fields) > 0:
                if fields_section:
                    fields_section.clear()
                    fields_table = BeautifulSoup('<table class="members" id="fieldList"><tr><th class="iconColumn"></th><th>Name</th><th>Description</th></tr></table>', PARSER).table
                    
                    for field in fields:
                        tr = soup.new_tag('tr')
                        
                        # Icon column
                        td_icon = soup.new_tag('td')
                        td_icon.append(soup.new_tag('img', attrs={
                            'src': '../icons/pubfield.gif',
                            'alt': 'Public field',
                            'title': 'Public field'
                        }))
                        tr.append(td_icon)
                        
                        # Name column
                        td_name = soup.new_tag('td')
                        a_tag = soup.new_tag('a', attrs={
                            'href': f"F_{full_name_underscored}_{field['name']}.htm"
                        })
                        a_tag.string = field['name']
                        td_name.append(a_tag)
                        tr.append(td_name)
                        
                        # Description column
                        td_desc = soup.new_tag('td')
                        div_summary_html = f'''<div class="summary">{field['summary']}</div>'''
                        div_summary_parsed = BeautifulSoup(div_summary_html, PARSER)
                        td_desc.append(div_summary_parsed)
                        tr.append(td_desc)
                        
                        fields_table.append(tr)
                    
                    fields_section.append(fields_table)
                    top_link = soup.new_tag('a', attrs={'href': '#PageHeader'})
                    top_link.string = 'Top'
                    fields_section.append(top_link)
            else:
                # Remove both the region header and section content for empty fields
                if fields_region:
                    fields_region.decompose()
                if fields_section:
                    fields_section.decompose()
            
            # See Also section
            see_also_section = soup.select_one('div#ID8RBSection')
            
            # Add JavaDoc remarks section before "See Also" if we have JavaDoc content
            see_also_container = soup.select_one('div#seeAlsoSection')
            if see_also_container and javadoc_remarks and javadoc_remarks != "To be added.":
                # Create a new remarks section
                remarks_region = soup.new_tag('div', attrs={'class': 'collapsibleAreaRegion', 'id': 'remarksSection'})
                remarks_title = soup.new_tag('span', attrs={
                    'class': 'collapsibleRegionTitle',
                    'onclick': "SectionExpandCollapse('ID7RB')",
                    'onkeypress': "SectionExpandCollapse_CheckKey('ID7RB', event)",
                    'tabindex': '0'
                })
                
                # Add the toggle icon and title
                toggle_img = soup.new_tag('img', attrs={
                    'id': 'ID7RBToggle',
                    'class': 'collapseToggle',
                    'src': '../icons/SectionExpanded.png'
                })
                remarks_title.append(toggle_img)
                remarks_title.append(soup.new_string('Remarks'))
                remarks_region.append(remarks_title)
                
                # Create the content section
                remarks_content_div = soup.new_tag('div', attrs={'id': 'ID7RBSection', 'class': 'collapsibleSection'})
                
                # Parse and add the JavaDoc remarks content
                if '<' in javadoc_remarks and '>' in javadoc_remarks:
                    remarks_soup = BeautifulSoup(javadoc_remarks, PARSER)
                    for element in remarks_soup.children:
                        if hasattr(element, 'name'):  # It's a tag
                            remarks_content_div.append(element)
                        else:  # It's text
                            remarks_content_div.append(soup.new_string(str(element)))
                else:
                    remarks_content_div.append(soup.new_string(javadoc_remarks))
                
                remarks_region.append(remarks_content_div)
                
                # Insert before the "See Also" section
                see_also_container.insert_before(remarks_region)
            
            if see_also_section and '{{ID8RBSection}}' in see_also_section.text:
                see_also_section.clear()
                see_also_section.append(BeautifulSoup(f'<h4 class="subHeading">Reference</h4><div class="seeAlsoStyle"><a href="N_{namespace.replace(".", "_")}.htm">{namespace} Namespace</a></div>', PARSER))
            
            # Update remarks
            remarks_section = soup.select_one('div#ID7RBSection')
            if remarks_section:
                remarks_section.clear()
                remarks_content = remarks if remarks else "To be added."
                if remarks_content:
                    remarks_content += "<p>"
                # Add Android documentation link with corrected path
                # Android docs use lowercase package names, so we need to lowercase the namespace
                android_namespace = 'com/datalogic/' + '/'.join(namespace.split('.')[2:]).lower()
                android_doc_link = f'<a href="http://datalogic.github.io/android-sdk-docs/reference/{android_namespace}/{type_name}.html" target="_blank">[Android Documentation]</a>'
                remarks_content += android_doc_link + "</p>"
                remarks_section.append(BeautifulSoup(remarks_content, PARSER))
            
            # Generate HTML from updated soup
            output_html = str(soup)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            # Write the output file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(output_html)
            
            
        except Exception as e:
            logger.error(f"Error generating HTML for {xml_file_path}: {str(e)}")
            raise
    
    def generate_component_files(self, xml_root):
        """Generate component files (Properties, Methods, individual pages) for a class."""
        try:
            type_name = xml_root.get('Name')
            full_name = xml_root.get('FullName')
            full_name_underscored = full_name.replace('.', '_')
            namespace = '.'.join(full_name.split('.')[:-1])
            
            # Extract members by type
            constructors = []
            properties = []
            methods = []
            fields = []
            
            for member in xml_root.findall('./Members/Member'):
                member_type_elem = member.find('./MemberType')
                member_type = member_type_elem.text if member_type_elem is not None else None
                member_name = member.get('MemberName')
                
                # Get documentation for this member
                member_docs = member.find('./Docs')
                member_summary = ""
                if member_docs is not None and member_docs.find('./summary') is not None:
                    member_summary = member_docs.find('./summary').text or ""
                
                member_info = {
                    'name': member_name,
                    'summary': member_summary if member_summary else "To be added.",
                    'element': member
                }
                
                if member_type == 'Constructor':
                    member_info['summary'] = f"Initializes a new instance of the {type_name} class"
                    constructors.append(member_info)
                elif member_type == 'Property':
                    properties.append(member_info)
                elif member_type == 'Method':
                    methods.append(member_info)
                elif member_type == 'Field':
                    fields.append(member_info)
            
            # Generate Properties list page if properties exist
            if properties:
                self.generate_properties_page(type_name, full_name, namespace, properties)
                
                # Generate individual property pages
                for prop in properties:
                    self.generate_property_page(type_name, full_name, namespace, prop, properties)
            
            # Generate Methods list page if methods exist
            if methods:
                self.generate_methods_page(type_name, full_name, namespace, methods)
                
                # Generate individual method pages
                for method in methods:
                    self.generate_method_page(type_name, full_name, namespace, method, methods)
            
            # Generate individual field pages if fields exist
            if fields:
                for field in fields:
                    self.generate_field_page(type_name, full_name, namespace, field, fields)
                    
        except Exception as e:
            logger.error(f"Error generating component files: {str(e)}")
            raise
    
    def generate_namespace_pages(self):
        """Generate namespace pages (N_*.htm files) for all namespaces."""
        logger.info(f"Generating namespace pages for {len(self.namespaces)} namespaces...")
        
        for namespace_name, types_info in self.namespaces.items():
            try:
                self.generate_namespace_page(namespace_name, types_info)
            except Exception as e:
                logger.error(f"Error generating namespace page for {namespace_name}: {str(e)}")
    
    def generate_namespace_page(self, namespace_name, types_info):
        """Generate a single namespace page (N_*.htm file)."""
        try:
            # Generate file ID (e.g., N_Com_Datalogic_Cradle)
            file_id = f"N_{namespace_name.replace('.', '_')}"
            
            # Load namespace template - use get_template_content to get raw HTML string
            from template_helper import get_template_content
            html_str = get_template_content('namespace', templates_dir=self.html_template_path)
            
            if not html_str:
                logger.error(f"Failed to load namespace template")
                return
            
            # Generate TOC entries for all types in this namespace
            toc_html = self.generate_namespace_toc(namespace_name, types_info)
            
            # Generate classes section
            classes_html = self.generate_namespace_classes_section(namespace_name, types_info['classes'])
            
            # Generate interfaces section
            interfaces_html = self.generate_namespace_interfaces_section(namespace_name, types_info['interfaces'])
            
            # Generate namespace summary (try to get from JavaDoc if available)
            namespace_summary = ""  # Could be enhanced to pull from JavaDoc
            
            # Replace placeholders
            html_str = html_str.replace('{{NAMESPACE}}', namespace_name)
            html_str = html_str.replace('{{FILE_ID}}', file_id)
            html_str = html_str.replace('{{TOC_TYPES}}', toc_html)
            html_str = html_str.replace('{{CLASSES_SECTION}}', classes_html)
            html_str = html_str.replace('{{INTERFACES_SECTION}}', interfaces_html)
            html_str = html_str.replace('{{NAMESPACE_SUMMARY}}', namespace_summary)
            
            # Write the file
            output_file = os.path.join(self.output_path, f"{file_id}.htm")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_str)
            
            logger.info(f"Generated namespace page: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating namespace page for {namespace_name}: {str(e)}")
            raise
    
    def generate_namespace_toc(self, namespace_name, types_info):
        """Generate TOC entries for all types in a namespace."""
        toc_html = []
        
        # Combine all types and sort them
        all_types = []
        for class_name in types_info['classes']:
            all_types.append((class_name, 'Class'))
        for interface_name in types_info['interfaces']:
            all_types.append((interface_name, 'Interface'))
        for enum_name in types_info.get('enums', []):
            all_types.append((enum_name, 'Enum'))
        
        all_types.sort(key=lambda x: x[0])
        
        for type_name, type_kind in all_types:
            full_name = f"{namespace_name}.{type_name}"
            file_id = f"T_{full_name.replace('.', '_')}"
            
            toc_html.append(f'''<div class="toclevel2" data-toclevel="2">
                    <a class="tocCollapsed" onclick="javascript: Toggle(this);" href="#!" />
                    <a data-tochassubtree="true" href="../html/{file_id}.htm" title="{type_name} {type_kind}" tocid="{file_id}">{type_name} {type_kind}</a>
                </div>''')
        
        return '\n'.join(toc_html)
    
    def generate_namespace_classes_section(self, namespace_name, classes):
        """Generate the classes section for a namespace page."""
        if not classes:
            return ""
        
        # Sort classes alphabetically
        sorted_classes = sorted(classes)
        
        rows = []
        for class_name in sorted_classes:
            full_name = f"{namespace_name}.{class_name}"
            file_id = f"T_{full_name.replace('.', '_')}"
            
            # Try to get javadoc summary for the class
            java_class_name = full_name.replace('.', '/')
            summary, _ = self.extract_javadoc_description(java_class_name)
            
            if not summary or summary == "To be added.":
                # Try to get Android documentation link
                java_package = namespace_name.lower().replace('.', '/')
                java_class = class_name
                summary = f'<a href="http://datalogic.github.io/android-sdk-docs/reference/{java_package}/{java_class}.html" target="_blank">[Android Documentation]</a>'
            
            rows.append(f'''<tr data="class; public">
                    <td><img src="../icons/pubclass.gif" alt="Public class" title="Public class" /></td>
                    <td><a href="{file_id}.htm">{class_name}</a></td>
                    <td><div class="summary">{summary}</div></td>
                </tr>''')
        
        classes_section = f'''<div class="collapsibleAreaRegion">
                <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID0RB')" onkeypress="SectionExpandCollapse_CheckKey('ID0RB', event)" tabindex="0">
                    <img id="ID0RBToggle" class="collapseToggle" src="../icons/SectionExpanded.png" />Classes
                </span>
            </div>
            <div id="ID0RBSection" class="collapsibleSection">
                <table class="members" id="classList">
                    <tr>
                        <th class="iconColumn"> </th>
                        <th>Class</th>
                        <th>Description</th>
                    </tr>
                    {''.join(rows)}
                </table>
            </div>'''
        
        return classes_section
    
    def generate_namespace_interfaces_section(self, namespace_name, interfaces):
        """Generate the interfaces section for a namespace page."""
        if not interfaces:
            return ""
        
        # Sort interfaces alphabetically
        sorted_interfaces = sorted(interfaces)
        
        rows = []
        for interface_name in sorted_interfaces:
            full_name = f"{namespace_name}.{interface_name}"
            file_id = f"T_{full_name.replace('.', '_')}"
            
            # Try to get javadoc summary for the interface
            java_class_name = full_name.replace('.', '/')
            summary, _ = self.extract_javadoc_description(java_class_name)
            
            if not summary or summary == "To be added.":
                # Try to get Android documentation link
                # Remove 'I' prefix if present for Java interface name
                java_interface = interface_name[1:] if interface_name.startswith('I') else interface_name
                java_package = namespace_name.lower().replace('.', '/')
                summary = f'<a href="http://datalogic.github.io/android-sdk-docs/reference/{java_package}/{java_interface}.html" target="_blank">[Android Documentation]</a>'
            
            rows.append(f'''<tr data="interface; public">
                    <td><img src="../icons/pubinterface.gif" alt="Public interface" title="Public interface" /></td>
                    <td><a href="{file_id}.htm">{interface_name}</a></td>
                    <td><div class="summary">{summary}</div></td>
                </tr>''')
        
        interfaces_section = f'''<div class="collapsibleAreaRegion">
                <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID1RB')" onkeypress="SectionExpandCollapse_CheckKey('ID1RB', event)" tabindex="0">
                    <img id="ID1RBToggle" class="collapseToggle" src="../icons/SectionExpanded.png" />Interfaces
                </span>
            </div>
            <div id="ID1RBSection" class="collapsibleSection">
                <table class="members" id="interfaceList">
                    <tr>
                        <th class="iconColumn"> </th>
                        <th>Interface</th>
                        <th>Description</th>
                    </tr>
                    {''.join(rows)}
                </table>
            </div>'''
        
        return interfaces_section
    
    def generate_properties_page(self, type_name, full_name, namespace, properties):
        """Generate the Properties_T_ClassName.htm page."""
        try:
            full_name_underscored = full_name.replace('.', '_')
            html_filename = f"Properties_T_{full_name_underscored}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Load properties template
            soup = get_template('properties', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load properties template")
                return
            
            # Generate properties table
            properties_table = '<table class="members" id="propertyList">\n'
            properties_table += '<tr><th class="iconColumn"> </th><th>Name</th><th>Description</th></tr>\n'
            
            for prop in properties:
                properties_table += f'''<tr data="public;declared;notNetfw;">
                    <td><img alt="Public property" src="../icons/pubproperty.gif" title="Public property" /></td>
                    <td><a href="P_{full_name_underscored}_{prop['name']}.htm">{prop['name']}</a></td>
                    <td><div class="summary">{prop['summary']}</div></td>
                </tr>\n'''
            
            properties_table += '</table>\n<a href="#PageHeader">Top</a>'
            
            # Replace placeholders
            self.replace_template_placeholders(soup, {
                'TYPE_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'FILE_NAME': f"Properties_T_{full_name_underscored}",
                'TYPE_LINK': f"T_{full_name_underscored}.htm",
                'NAMESPACE_LINK': f"N_{namespace.replace('.', '_')}.htm",
                'PROPERTIES_TABLE': properties_table
            })
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            
        except Exception as e:
            logger.error(f"Error generating properties page: {str(e)}")
    
    def generate_methods_page(self, type_name, full_name, namespace, methods):
        """Generate the Methods_T_ClassName.htm page."""
        try:
            full_name_underscored = full_name.replace('.', '_')
            html_filename = f"Methods_T_{full_name_underscored}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Load methods template
            soup = get_template('methods', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load methods template")
                return
            
            # Generate methods table
            methods_table = '<table class="members" id="methodList">\n'
            methods_table += '<tr><th class="iconColumn"> </th><th>Name</th><th>Description</th></tr>\n'
            
            for method in methods:
                methods_table += f'''<tr data="public;declared;notNetfw;">
                    <td><img alt="Public method" src="../icons/pubmethod.gif" title="Public method" /></td>
                    <td><a href="M_{full_name_underscored}_{method['name']}.htm">{method['name']}</a></td>
                    <td><div class="summary">{method['summary']}</div></td>
                </tr>\n'''
            
            methods_table += '</table>\n<a href="#PageHeader">Top</a>'
            
            # Replace placeholders
            self.replace_template_placeholders(soup, {
                'TYPE_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'FILE_NAME': f"Methods_T_{full_name_underscored}",
                'CLASS_FILE_NAME': f"T_{full_name_underscored}.htm",
                'METHODS_TABLE': methods_table
            })
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            
        except Exception as e:
            logger.error(f"Error generating methods page: {str(e)}")
    
    def generate_property_page(self, type_name, full_name, namespace, prop, all_properties=None):
        """Generate individual P_ClassName_PropertyName.htm pages."""
        try:
            full_name_underscored = full_name.replace('.', '_')
            html_filename = f"P_{full_name_underscored}_{prop['name']}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Load property template
            soup = get_template('property', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load property template")
                return
            
            # Convert full_name to Java class name format (same as methods)
            java_class_name = full_name.replace('Com.', 'com.').replace('Datalogic.', 'datalogic.').replace('Decode.', 'decode.')
            # Extract all JavaDoc content for this method at once
            javadoc_details = self.extract_javadoc_method_details(java_class_name, prop['name'])
            summary = javadoc_details['summary']
            remarks = javadoc_details['remarks']


            # For properties, we need to find the getter method in JavaDoc
            # Boolean properties typically use "isPropertyName", others use "getPropertyName"
            prop_element = prop['element']
            return_value = prop_element.find('./ReturnValue/ReturnType')
            is_boolean = False
            
            if return_value is not None:
                full_return_type = return_value.text
                if full_return_type == "System.Boolean":
                    is_boolean = True
            
            # Fallback to empty details if no JavaDoc found
            if javadoc_details is None:
                javadoc_details = {
                    'summary': prop['summary'],
                    'remarks': '',
                    'parameters': [],
                    'return_value': '',
                    'exceptions': []
                }
            
            # Generate navigation entries for all properties (following method pattern)
            property_nav_entries = []
            if all_properties:
                for p in all_properties:
                    property_filename = f"P_{full_name_underscored}_{p['name']}"
                    is_current = p['name'] == prop['name']
                    css_class = 'toclevel2 current' if is_current else 'toclevel2'
                    
                    property_nav_entries.append(f'''<div class="{css_class}" data-toclevel="2">
            <a data-tochassubtree="false" href="../html/{property_filename}.htm" title="{p['name']} Property" tocid="{property_filename}">{p['name']} Property</a>
          </div>''')
            
            properties_navigation = '\n          '.join(property_nav_entries)
            
            # Generate detailed syntax section (reuse method syntax logic but for properties)
            syntax_section = self.generate_property_syntax(prop_element, prop['name'])
            
            # Generate property value section (custom for properties, not using method return value)
            property_value_section = self.generate_property_value_section(prop_element, java_class_name, prop['name'], javadoc_details['return_value'])
            
            # Generate exceptions section if property throws exceptions (reuse method logic)
            exceptions_section = self.generate_method_exceptions(prop_element, java_class_name, prop['name'], javadoc_details['exceptions'])
            
            # Generate remarks section with JavaDoc content and Android documentation link
            remarks_section = ""
            if remarks:
                android_doc_link = f"http://datalogic.github.io/android-sdk-docs/reference/{java_class_name.replace('.', '/')}.html#{prop['name'].lower()}()"
                remarks_with_link = f"{remarks}<p><a href=\"{android_doc_link}\" target=\"_blank\">[Android Documentation]</a></p>"
                
                remarks_section = f'''
        <div class="collapsibleSection" id="ID3RBSection">
          {remarks_with_link}
        </div>'''
            
            # Replace placeholders (following method pattern)
            self.replace_template_placeholders(soup, {
                'MEMBER_NAME': prop['name'],
                'CLASS_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'FILE_NAME': f"P_{full_name_underscored}_{prop['name']}",
                'SUMMARY': summary if summary else prop['summary'],
                'CLASS_FILE_NAME': full_name_underscored,
                'NAMESPACE_LINK': f"N_{namespace.replace('.', '_')}.htm",
                'CLASS_LINK': f"T_{full_name_underscored}.htm",
                'SYNTAX_SECTION': syntax_section,
                'PROPERTY_VALUE_SECTION': property_value_section,  # This is the "return value" for properties
                'EXCEPTIONS_SECTION': exceptions_section,
                'REMARKS_SECTION': remarks_section,
                'PROPERTIES_NAVIGATION': properties_navigation
            })
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
        except Exception as e:
            logger.error(f"Error generating property page for {prop['name']}: {str(e)}")
    
    def generate_property_syntax(self, prop_element, prop_name):
        """Generate detailed property syntax section with language tabs (adapted from method syntax)."""
        # Extract property signature information
        cs_signature = prop_element.find(".//MemberSignature[@Language='C#']")
        if cs_signature is not None:
            cs_value = cs_signature.get('Value', f'public {prop_name} {{ get; }}')
        else:
            cs_value = f'public {prop_name} {{ get; }}'
        
        # Generate VB.NET syntax from C# signature
        vb_value = self.format_code_syntax_vb(cs_value)
        
        # Generate syntax with proper formatting (same structure as methods)
        syntax_html = f'''<div class="codeSnippetContainer">
            <div class="codeSnippetContainerTabs">
                <div id="ID0EBCA_tab1" class="codeSnippetContainerTab">
                    <a href="#" onclick="javascript:ChangeTab('ID0EBCA','cs','1','2');return false;">C#</a>
                </div>
                <div id="ID0EBCA_tab2" class="codeSnippetContainerTab">
                    <a href="#" onclick="javascript:ChangeTab('ID0EBCA','vb','2','2');return false;">VB</a>
                </div>
            </div>
            <div class="codeSnippetContainerCodeContainer">
                <div class="codeSnippetToolBar">
                    <div class="codeSnippetToolBarText">
                        <a id="ID0EBCA_copyCode" href="#" class="copyCodeSnippet" onclick="javascript:CopyToClipboard('ID0EBCA');return false;" title="Copy">Copy</a>
                    </div>
                </div>
                <div id="ID0EBCA_code_Div1" class="codeSnippetContainerCode" style="display: block">
                    <pre xml:space="preserve">{self.format_code_syntax(cs_value)}</pre>
                </div>
                <div id="ID0EBCA_code_Div2" class="codeSnippetContainerCode" style="display: none">
                    <pre xml:space="preserve">{vb_value}</pre>
                </div>
            </div>
        </div>
        <script type="text/javascript">AddLanguageTabSet("ID0EBCA");</script>'''
        
        return syntax_html
    
    def generate_property_value_section(self, prop_element, java_class_name, method_name, javadoc_return_value):
        """Generate return value section for method."""
        return_value = prop_element.find(".//ReturnValue/ReturnType")
        if return_value is not None and return_value.text and return_value.text != "System.Void":
            return_type = return_value.text
            
            # Get return documentation from JavaDoc - use pre-extracted if available
            if javadoc_return_value is None:
                return_desc = self.extract_javadoc_return_value(java_class_name, method_name)
            else:
                return_desc = javadoc_return_value
                
            if not return_desc:
                return_desc = "No description available."
            
            return f'''<h4 class="subHeading">Property Value</h4>
                <p>Type: <a href="#">{return_type}</a><br />{return_desc}</p>'''
        return ""

    def generate_method_page(self, type_name, full_name, namespace, method, all_methods):
        """Generate individual M_ClassName_MethodName.htm pages."""
        try:
            full_name_underscored = full_name.replace('.', '_')
            html_filename = f"M_{full_name_underscored}_{method['name']}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Load method template
            soup = get_template('method', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load method template")
                return
            
            # Convert full_name to Java class name format (e.g., Com.Datalogic.Decode.BarcodeManager -> com.datalogic.decode.BarcodeManager)
            java_class_name = full_name.replace('Com.', 'com.').replace('Datalogic.', 'datalogic.').replace('Decode.', 'decode.')
            
            # Extract all JavaDoc content for this method at once
            javadoc_details = self.extract_javadoc_method_details(java_class_name, method['name'])
            summary = javadoc_details['summary']
            remarks = javadoc_details['remarks']
            
            # Generate navigation entries for all methods
            method_nav_entries = []
            for m in all_methods:
                method_filename = f"M_{full_name_underscored}_{m['name']}"
                is_current = m['name'] == method['name']
                css_class = 'toclevel2 current' if is_current else 'toclevel2'
                
                method_nav_entries.append(f'''<div class="{css_class}" data-toclevel="2">
            <a data-tochassubtree="false" href="../html/{method_filename}.htm" title="{m['name']} Method" tocid="{method_filename}">{m['name']} Method</a>
          </div>''')
            
            methods_navigation = '\n          '.join(method_nav_entries)
            
            # Extract method details from XML
            method_element = method['element']
            
            # Generate detailed syntax section
            syntax_section = self.generate_method_syntax(method_element, method['name'])
            
            # Generate parameters section if method has parameters
            parameters_section = self.generate_method_parameters(method_element, java_class_name, method['name'], javadoc_details['parameters'])
            
            # Generate return value section if method returns something
            return_value_section = self.generate_method_return_value(method_element, java_class_name, method['name'], javadoc_details['return_value'])
            
            # Generate exceptions section if method throws exceptions
            exceptions_section = self.generate_method_exceptions(method_element, java_class_name, method['name'], javadoc_details['exceptions'])
            
            # Generate remarks section with JavaDoc content and Android documentation link
            remarks_section = ""
            if remarks:
                android_doc_link = f"http://datalogic.github.io/android-sdk-docs/reference/{java_class_name.replace('.', '/')}.html#{method['name'].lower()}"
                remarks_with_link = f"{remarks}<p><a href=\"{android_doc_link}\" target=\"_blank\">[Android Documentation]</a></p>"
                
                remarks_section = f'''<div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID3RB')" onkeypress="SectionExpandCollapse_CheckKey('ID3RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID3RBToggle" src="../icons/SectionExpanded.png" />Remarks
          </span>
        </div>
        <div class="collapsibleSection" id="ID3RBSection">
          {remarks_with_link}
        </div>'''
            
            # Replace placeholders
            self.replace_template_placeholders(soup, {
                'MEMBER_NAME': method['name'],
                'CLASS_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'FILE_NAME': f"M_{full_name_underscored}_{method['name']}",
                'SUMMARY': summary if summary else method['summary'],
                'CLASS_FILE_NAME': full_name_underscored,
                'NAMESPACE_LINK': namespace.replace('.', '_'),
                'SYNTAX_SECTION': syntax_section,
                'PARAMETERS_SECTION': parameters_section,
                'RETURN_VALUE_SECTION': return_value_section,
                'EXCEPTIONS_SECTION': exceptions_section,
                'REMARKS_SECTION': remarks_section,
                'METHODS_NAVIGATION': methods_navigation,
                'PARAMETER_SIGNATURE': '',  # Will be generated properly later
                'UNIQUE_ID': 'METHOD',  # Simple unique ID for now
                'SEEALSO_ID': '4'  # ID for see also section
            })
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            
        except Exception as e:
            logger.error(f"Error generating method page for {method['name']}: {str(e)}")
    
    def generate_method_syntax(self, method_element, method_name):
        """Generate detailed method syntax section with language tabs."""
        # Extract method signature information
        cs_signature = method_element.find(".//MemberSignature[@Language='C#']")
        if cs_signature is not None:
            cs_value = cs_signature.get('Value', '')
        else:
            cs_value = f"public virtual void {method_name}()"
        
        # Generate syntax with proper formatting
        syntax_html = f'''<div class="codeSnippetContainer">
            <div class="codeSnippetContainerTabs">
                <div id="ID0EBCA_tab1" class="codeSnippetContainerTab">
                    <a href="#" onclick="javascript:ChangeTab('ID0EBCA','cs','1','2');return false;">C#</a>
                </div>
                <div id="ID0EBCA_tab2" class="codeSnippetContainerTab">
                    <a href="#" onclick="javascript:ChangeTab('ID0EBCA','vb','2','2');return false;">VB</a>
                </div>
            </div>
            <div class="codeSnippetContainerCodeContainer">
                <div class="codeSnippetToolBar">
                    <div class="codeSnippetToolBarText">
                        <a id="ID0EBCA_copyCode" href="#" class="copyCodeSnippet" onclick="javascript:CopyToClipboard('ID0EBCA');return false;" title="Copy">Copy</a>
                    </div>
                </div>
                <div id="ID0EBCA_code_Div1" class="codeSnippetContainerCode" style="display: block">
                    <pre xml:space="preserve">{self.format_code_syntax(cs_value)}</pre>
                </div>
                <div id="ID0EBCA_code_Div2" class="codeSnippetContainerCode" style="display: none">
                    <pre xml:space="preserve">{self.format_code_syntax_vb(cs_value)}</pre>
                </div>
            </div>
        </div>
        <script type="text/javascript">AddLanguageTabSet("ID0EBCA");</script>'''
        
        return syntax_html
    
    def generate_method_parameters(self, method_element, java_class_name, method_name, javadoc_params=None):
        """Generate parameters section for method."""
        parameters = method_element.findall(".//Parameter")
        if not parameters:
            return ""
        
        # Get JavaDoc parameter descriptions - use pre-extracted if available
        if javadoc_params is None:
            javadoc_params = self.extract_javadoc_parameters(java_class_name, method_name)
        javadoc_param_dict = {p['name']: p['description'] for p in javadoc_params}
        
        params_html = '<h4 class="subHeading">Parameters</h4><dl class="parameterList">'
        for param in parameters:
            param_name = param.get('Name', '')
            param_type = param.get('Type', '')
            
            # Get parameter documentation from JavaDoc if available
            param_desc = javadoc_param_dict.get(param_name, "No description available.")
            
            params_html += f'''<dt><span class="parameter">{param_name}</span></dt>
                <dd>Type: <a href="#">{param_type}</a><br />{param_desc}</dd>'''
        
        params_html += '</dl>'
        return params_html
    
    def generate_method_return_value(self, method_element, java_class_name, method_name, javadoc_return_value=None):
        """Generate return value section for method."""
        return_value = method_element.find(".//ReturnValue/ReturnType")
        if return_value is not None and return_value.text and return_value.text != "System.Void":
            return_type = return_value.text
            
            # Get return documentation from JavaDoc - use pre-extracted if available
            if javadoc_return_value is None:
                return_desc = self.extract_javadoc_return_value(java_class_name, method_name)
            else:
                return_desc = javadoc_return_value
                
            if not return_desc:
                return_desc = "No description available."
            
            return f'''<h4 class="subHeading">Return Value</h4>
                <p>Type: <a href="#">{return_type}</a><br />{return_desc}</p>'''
        return ""
    
    def generate_method_exceptions(self, method_element, java_class_name, method_name, javadoc_exceptions=None):
        """Generate exceptions section for method."""
        # Get exceptions from JavaDoc - use pre-extracted if available
        if javadoc_exceptions is None:
            javadoc_exceptions = self.extract_javadoc_exceptions(java_class_name, method_name)
        
        if not javadoc_exceptions:
            return ""
        
        exceptions_html = '''<div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID2RB')" onkeypress="SectionExpandCollapse_CheckKey('ID2RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID2RBToggle" src="../icons/SectionExpanded.png" />Exceptions
          </span>
        </div>
        <div class="collapsibleSection" id="ID2RBSection">
          <div class="tableContainer">
            <table class="dtTABLE">
              <tr valign="top">
                <th>Exception</th>
                <th>Condition</th>
              </tr>'''
        
        for exception in javadoc_exceptions:
            exc_type = exception['type']
            exc_desc = exception['description']
            exceptions_html += f'''<tr valign="top">
                <td><a href="#">{exc_type}</a></td>
                <td>{exc_desc}</td>
              </tr>'''
        
        exceptions_html += '''</table>
          </div>
        </div>'''
        
        return exceptions_html
    
    def format_code_syntax(self, code):
        """Format C# code with proper syntax highlighting."""
        # Simple syntax highlighting - can be enhanced
        code = code.replace('public', '<span class="keyword">public</span>')
        code = code.replace('virtual', '<span class="keyword">virtual</span>')
        code = code.replace('static', '<span class="keyword">static</span>')
        code = code.replace('void', '<span class="keyword">void</span>')
        code = code.replace('int', '<span class="keyword">int</span>')
        code = code.replace('string', '<span class="keyword">string</span>')
        code = code.replace('bool', '<span class="keyword">bool</span>')
        return code
    
    def format_code_syntax_vb(self, cs_code):
        """Convert C# code to VB.NET syntax (simplified)."""
        # Very basic C# to VB conversion - can be enhanced
        vb_code = cs_code.replace('public', 'Public')
        vb_code = vb_code.replace('virtual', 'Virtual')
        vb_code = vb_code.replace('void', 'Sub')
        vb_code = vb_code.replace('int', 'Integer')
        vb_code = vb_code.replace('string', 'String')
        vb_code = vb_code.replace('bool', 'Boolean')
        vb_code = vb_code.replace('{', '')
        vb_code = vb_code.replace('}', 'End Sub')
        return vb_code
    
    def generate_field_page(self, type_name, full_name, namespace, field, all_fields):
        """Generate individual F_ClassName_FieldName.htm pages."""
        try:
            full_name_underscored = full_name.replace('.', '_')
            html_filename = f"F_{full_name_underscored}_{field['name']}.htm"
            output_file_path = os.path.join(self.output_path, html_filename)
            
            # Load field template
            soup = get_template('field', templates_dir=self.html_template_path)
            if soup is None:
                logger.error(f"Could not load field template")
                return
            
            # Extract JavaDoc documentation for this field
            # Convert .NET namespace to Java package name: Com.Datalogic.Decode -> com.datalogic.decode
            java_package = namespace.lower()
            # Convert nested class separator from + to . (e.g., DLCradleManager+Properties -> DLCradleManager.Properties)
            java_type_name = type_name.replace('+', '.')
            java_class_name = f"{java_package}.{java_type_name}"
            
            # Get the Java field name from the Android.Runtime.Register attribute
            java_field_name = field['name']  # Default to C# name
            if 'element' in field:
                attributes = field['element'].find('./Attributes')
                if attributes:
                    for attr in attributes.findall('.//Attribute'):
                        attr_name = attr.find('./AttributeName')
                        if attr_name is not None and 'Android.Runtime.Register' in attr_name.text:
                            # Extract the field name from the attribute
                            attr_text = attr_name.text
                            if '"' in attr_text:
                                java_field_name = attr_text.split('"')[1]
                                break
            
            # Store java names in field for syntax generation
            field['java_class_name'] = java_class_name  
            field['java_field_name'] = java_field_name
            
            field_summary, field_remarks = self.extract_javadoc_description(java_class_name, java_field_name)
            
            
            # Use JavaDoc content if available, otherwise fall back to mdoc
            summary = field_summary if field_summary else field['summary']
            remarks = field_remarks if field_remarks else field['summary']
            
            # Ensure we have proper fallback content
            if not summary or summary == "To be added.":
                summary = f"{field['name']} field description."
            if not remarks or remarks == "To be added.":
                remarks = summary
            
            # Generate navigation entries for all fields
            field_nav_entries = []
            for f in all_fields:
                field_filename = f"F_{full_name_underscored}_{f['name']}"
                is_current = f['name'] == field['name']
                css_class = 'toclevel2 current' if is_current else 'toclevel2'
                
                field_nav_entries.append(f'''<div class="{css_class}" data-toclevel="2">
            <a data-tochassubtree="false" href="../html/{field_filename}.htm" title="{f['name']} Field" tocid="{field_filename}">{f['name']} Field</a>
          </div>''')
            
            fields_navigation = '\n          '.join(field_nav_entries)
            
            # Create proper remarks section if we have content
            remarks_section = ""
            if remarks and remarks.strip():
                # Add Android documentation link
                android_doc_link = f'<p><a href="http://datalogic.github.io/android-sdk-docs/reference/{java_class_name.replace(".", "/")}.html#{java_field_name}" target="_blank">[Android Documentation]</a></p>'
                full_remarks = f'{remarks}{android_doc_link}'
                
                remarks_section = f'''<div class="collapsibleAreaRegion">
          <span class="collapsibleRegionTitle" onclick="SectionExpandCollapse('ID3RB')" onkeypress="SectionExpandCollapse_CheckKey('ID3RB', event)" tabindex="0">
            <img class="collapseToggle" id="ID3RBToggle" src="../icons/SectionExpanded.png" />Remarks
          </span>
        </div>
        <div class="collapsibleSection" id="ID3RBSection">
          {full_remarks}
        </div>'''
            
            # Replace placeholders
            self.replace_template_placeholders(soup, {
                'MEMBER_NAME': field['name'],
                'TYPE_NAME': type_name,
                'FULL_NAME': full_name,
                'FULL_NAME_UNDERSCORED': full_name_underscored,
                'NAMESPACE': namespace,
                'NAMESPACE_UNDERSCORED': namespace.replace('.', '_'),
                'FILE_NAME': f"F_{full_name_underscored}_{field['name']}",
                'SUMMARY': summary,
                'NAMESPACE_LINK': f"N_{namespace.replace('.', '_')}.htm",
                'ASSEMBLY_INFO': "datalogic-xamarin-sdk (in datalogic-xamarin-sdk.dll) Version: 1.0.0.0 (1.0.0.0)",
                'SYNTAX': self.generate_field_syntax(field),
                'FIELD_VALUE_SECTION': '',
                'REMARKS_SECTION': remarks_section,
                'SEE_ALSO': f'<h4 class="subHeading">Reference</h4><div class="seeAlsoStyle"><a href="T_{full_name_underscored}.htm">{type_name} Class</a></div><div class="seeAlsoStyle"><a href="N_{namespace.replace(".", "_")}.htm">{namespace} Namespace</a></div>',
                'FIELDS_NAVIGATION': fields_navigation,
                'FIELD_TITLE': f'{type_name}.{field["name"]} Field'
            })
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
        except Exception as e:
            logger.error(f"Error generating field page for {field['name']}: {str(e)}")
    
    def generate_field_syntax(self, field):
        """Generate proper syntax section for field pages with tabs and formatting."""
        field_name = field['name']
        
        # Get the field type and value from the XML if available
        field_type = "string"  # Default to string for most fields
        field_value = '"value"'  # Default value
        
        if 'element' in field:
            return_value = field['element'].find('./ReturnValue/ReturnType')
            if return_value is not None:
                full_type = return_value.text
                field_type = full_type.split('.')[-1] if '.' in full_type else full_type
            
            # Try to extract the actual field value from the JavaDoc
            java_class_name = field.get('java_class_name', '')
            java_field_name = field.get('java_field_name', field_name)
            
            if java_class_name and java_field_name:
                # Look for the field value in the JavaDoc content
                if java_class_name in self.javadoc_content:
                    soup = self.javadoc_content[java_class_name]
                    # Look for the field value in the field details section
                    field_details = soup.find('section', {'class': 'field-details'})
                    if field_details:
                        # Find the specific field
                        field_sections = field_details.find_all('section', {'class': 'detail'})
                        for section in field_sections:
                            field_heading = section.find('h3')
                            if field_heading and java_field_name in field_heading.get_text():
                                # Look for the field value
                                pre_element = section.find('pre')
                                if pre_element:
                                    text = pre_element.get_text()
                                    # Extract value from something like: public static final String ACTION_START_DECODE = "com.datalogic.decode.action.START_DECODE"
                                    if '=' in text:
                                        field_value = text.split('=')[1].strip().rstrip(';')
                                        break
        
        # Handle special case for ACTION_START_DECODE and ACTION_STOP_DECODE
        if field_name == 'ActionStartDecode':
            field_value = '"com.datalogic.decode.action.START_DECODE"'
        elif field_name == 'ActionStopDecode':
            field_value = '"com.datalogic.decode.action.STOP_DECODE"'
        
        syntax_html = f'''<div class="codeSnippetContainer">
          <div class="codeSnippetContainerTabs">
            <div id="ID0EBCA_tab1" class="codeSnippetContainerTab">
              <a href="#" onclick="javascript:ChangeTab('ID0EBCA','cs','1','2');return false;">C#</a>
            </div>
            <div id="ID0EBCA_tab2" class="codeSnippetContainerTab">
              <a href="#" onclick="javascript:ChangeTab('ID0EBCA','vb','2','2');return false;">VB</a>
            </div>
          </div>
          <div class="codeSnippetContainerCodeContainer">
            <div class="codeSnippetToolBar">
              <div class="codeSnippetToolBarText">
                <a id="ID0EBCA_copyCode" href="#" class="copyCodeSnippet" onclick="javascript:CopyToClipboard('ID0EBCA');return false;" title="Copy">Copy</a>
              </div>
            </div>
            <div id="ID0EBCA_code_Div1" class="codeSnippetContainerCode" style="display: block">
              <pre xml:space="preserve"><span class="keyword">public</span> <span class="keyword">const</span> <span class="identifier">{field_type}</span> <span class="identifier">{field_name}</span> = {field_value}</pre>
            </div>
            <div id="ID0EBCA_code_Div2" class="codeSnippetContainerCode" style="display: none">
              <pre xml:space="preserve"><span class="keyword">Public</span> <span class="keyword">Const</span> <span class="identifier">{field_name}</span> <span class="keyword">As</span> <span class="identifier">{field_type}</span> = {field_value}</pre>
            </div>
          </div>
        </div>
        <script type="text/javascript">AddLanguageTabSet("ID0EBCA");</script>
        <h4 class="subHeading">Field Value</h4>
        Type: <a href="https://docs.microsoft.com/dotnet/api/system.{field_type.lower()}" target="_blank">{field_type}</a>'''
        
        return syntax_html
    
    class JavaDocExtractor:
        """Handles extraction of different types of documentation from JavaDoc HTML."""
        
        def __init__(self, javadoc_content):
            self.javadoc_content = javadoc_content
        
        def _normalize_class_name(self, class_name):
            """Convert .NET class name to Java class name format."""
            if not class_name:
                return None
            
            if '/' in class_name or '\\' in class_name:
                java_class_name = class_name.replace('/', '.').replace('\\', '.')
            else:
                java_class_name = class_name
            
            return java_class_name
        
        def _find_class_soup(self, class_name):
            """Find and return the BeautifulSoup object for a class."""
            java_class_name = self._normalize_class_name(class_name)
            if not java_class_name:
                return None
            
            # Check if we have this class loaded
            if java_class_name not in self.javadoc_content:
                # Try case-insensitive matching
                for key in self.javadoc_content.keys():
                    if key.lower() == java_class_name.lower():
                        return self.javadoc_content[key]
                
                logger.debug(f"JavaDoc not found for class: {java_class_name}")
                return None
            
            return self.javadoc_content[java_class_name]
        
        def _extract_first_sentence(self, text):
            """Extract the first sentence from text for summary purposes, handling HTML properly."""
            if not text:
                return ""
            
            # If there's no HTML, use simple text processing
            if '<' not in text:
                first_sentence_match = re.search(r'^([^.]*\.)', text)
                if first_sentence_match:
                    return first_sentence_match.group(1).strip()
                else:
                    parts = text.split('.', 1)
                    return parts[0].strip() + '.' if parts else text
            
            # Handle HTML by iterating through characters and skipping tags
            result = []
            i = 0
            in_tag = False
            current_tag = None
            
            while i < len(text):
                char = text[i]
                
                if char == '<' and not in_tag:
                    # Start of a tag
                    in_tag = True
                    tag_start = i
                    result.append(char)
                    
                    # Read the tag name (until space or >)
                    j = i + 1
                    tag_name = ""
                    while j < len(text) and text[j] not in [' ', '>']:
                        tag_name += text[j]
                        j += 1
                    
                    current_tag = tag_name.lstrip('/')  # Remove leading slash for closing tags
                    
                elif char == '>' and in_tag:
                    # End of tag
                    result.append(char)
                    in_tag = False
                    current_tag = None
                    
                elif char == '.' and not in_tag:
                    # Found period outside of any tag - this ends our first sentence
                    result.append(char)
                    break
                    
                else:
                    # Regular character or character inside tag
                    result.append(char)
                
                i += 1
            
            return ''.join(result).strip()
        
        def extract_class_documentation(self, class_name):
            """Extract class-level documentation.
            
            Returns:
                tuple: (summary, remarks) - both containing full HTML content
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return ("", "")
            
            # Find the class description
            class_desc = soup.select_one('section.class-description div.block')
            if class_desc:
                desc_html = class_desc.decode_contents().strip()
                # For classes, return the same content for both summary and remarks
                return (desc_html, desc_html)
            
            # Try alternative selectors
            alt_selectors = ['div.description div.block', '.classDescription', '.summary']
            for selector in alt_selectors:
                alt_desc = soup.select_one(selector)
                if alt_desc:
                    desc_html = alt_desc.decode_contents().strip()
                    return (desc_html, desc_html)
            
            return ("", "")
        
        def extract_member_table_summary(self, class_name, member_name):
            """Extract brief summary for member tables.
            
            Returns:
                str: Brief summary suitable for table display
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return ""
            
            # Look in summary tables first (more concise)
            method_tables = soup.select('div.summary-table')
            for table in method_tables:
                member_links = table.select('a.member-name-link')
                for link in member_links:
                    link_text = link.get_text().strip()
                    if member_name.lower() == link_text.lower():
                        link_container = link.find_parent('div', class_='col-second')
                        if link_container:
                            desc_div = link_container.find_next_sibling('div', class_='col-last')
                            if desc_div:
                                desc_block = desc_div.select_one('div.block')
                                if desc_block:
                                    return desc_block.decode_contents().strip()
            
            # If not found in summary, try detail sections
            detail_sections = soup.select('section.detail')
            for detail in detail_sections:
                if detail.get('id', '').lower() == member_name.lower():
                    desc_block = detail.select_one('div.block')
                    if desc_block:
                        full_desc = desc_block.decode_contents().strip()
                        return self._extract_first_sentence(full_desc)
            
            return ""
        
        def extract_member_full_documentation(self, class_name, member_name):
            """Extract complete documentation for individual member pages.
            
            Returns:
                tuple: (summary, remarks) where summary is first sentence, remarks is full content
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return ("", "")
            
            # Look in detail sections first (most complete)
            detail_sections = soup.select('section.detail')
            for detail in detail_sections:
                detail_id = detail.get('id', '')
                # Extract method name before parenthesis for comparison
                method_name_part = detail_id.split('(')[0].lower() if '(' in detail_id else detail_id.lower()
                if method_name_part == member_name.lower():
                    desc_block = detail.select_one('div.block')
                    if desc_block:
                        full_desc = desc_block.decode_contents().strip()
                        summary = self._extract_first_sentence(full_desc)
                        return (summary, full_desc)
            
            # Fall back to summary tables
            return (self.extract_member_table_summary(class_name, member_name), "")
        
        def extract_method_parameters(self, class_name, method_name):
            """Extract parameter documentation for methods.
            
            Returns:
                list: List of {'name': str, 'description': str} dictionaries
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return []
            
            # Find the method detail section
            detail_sections = soup.select('section.detail')
            detail_section = None
            for detail in detail_sections:
                detail_id = detail.get('id', '')
                # Extract method name before parenthesis for comparison
                method_name_part = detail_id.split('(')[0].lower() if '(' in detail_id else detail_id.lower()
                if method_name_part == method_name.lower():
                    detail_section = detail
                    break
            
            if not detail_section:
                return []
            
            # Find the parameters section in dl.notes
            dl_notes = detail_section.find('dl', class_='notes')
            if not dl_notes:
                return []
            
            parameters = []
            dt_elements = dl_notes.find_all('dt')
            
            for dt in dt_elements:
                if dt.get_text(strip=True) == 'Parameters:':
                    dd = dt.find_next_sibling('dd')
                    while dd and dd.name == 'dd':
                        param_text = dd.get_text(separator=' ', strip=True)
                        code_elem = dd.find('code')
                        if code_elem:
                            param_name = code_elem.get_text(strip=True)
                            param_desc = param_text.replace(param_name, '', 1).strip()
                            if param_desc.startswith('-'):
                                param_desc = param_desc[1:].strip()
                            parameters.append({
                                'name': param_name,
                                'description': param_desc
                            })
                        
                        next_elem = dd.find_next_sibling(['dt', 'dd'])
                        if next_elem and next_elem.name == 'dt':
                            break
                        dd = next_elem if next_elem and next_elem.name == 'dd' else None
                    break
            
            return parameters
        
        def extract_method_return_value(self, class_name, method_name):
            """Extract return value documentation for methods.
            
            Returns:
                str: Return value description
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return ""
            
            # Find the method detail section
            detail_sections = soup.select('section.detail')
            detail_section = None
            for detail in detail_sections:
                detail_id = detail.get('id', '')
                # Extract method name before parenthesis for comparison
                method_name_part = detail_id.split('(')[0].lower() if '(' in detail_id else detail_id.lower()
                if method_name_part == method_name.lower():
                    detail_section = detail
                    break
            
            if not detail_section:
                return ""
            
            # Find the returns section in dl.notes
            dl_notes = detail_section.find('dl', class_='notes')
            if not dl_notes:
                return ""
            
            dt_elements = dl_notes.find_all('dt')
            for dt in dt_elements:
                if dt.get_text(strip=True) == 'Returns:':
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        return dd.get_text(separator=' ', strip=True)
            
            return ""
        
        def extract_method_exceptions(self, class_name, method_name):
            """Extract exceptions documentation for methods.
            
            Returns:
                list: List of {'type': str, 'description': str} dictionaries
            """
            soup = self._find_class_soup(class_name)
            if not soup:
                return []
            
            # Find the method detail section
            detail_sections = soup.select('section.detail')
            detail_section = None
            for detail in detail_sections:
                detail_id = detail.get('id', '')
                # Extract method name before parenthesis for comparison
                method_name_part = detail_id.split('(')[0].lower() if '(' in detail_id else detail_id.lower()
                if method_name_part == method_name.lower():
                    detail_section = detail
                    break
            
            if not detail_section:
                return []
            
            # Find the throws section in dl.notes
            dl_notes = detail_section.find('dl', class_='notes')
            if not dl_notes:
                return []
            
            exceptions = []
            dt_elements = dl_notes.find_all('dt')
            
            for dt in dt_elements:
                if dt.get_text(strip=True) == 'Throws:':
                    dd = dt.find_next_sibling('dd')
                    while dd and dd.name == 'dd':
                        exc_text = dd.get_text(separator=' ', strip=True)
                        code_elem = dd.find('code')
                        if code_elem:
                            exc_type = code_elem.get_text(strip=True)
                            exc_desc = exc_text.replace(exc_type, '', 1).strip()
                            if exc_desc.startswith('-'):
                                exc_desc = exc_desc[1:].strip()
                            exceptions.append({
                                'type': exc_type,
                                'description': exc_desc
                            })
                        
                        next_elem = dd.find_next_sibling(['dt', 'dd'])
                        if next_elem and next_elem.name == 'dt':
                            break
                        dd = next_elem if next_elem and next_elem.name == 'dd' else None
                    break
            
            return exceptions

def main():
    parser = argparse.ArgumentParser(description='Merge mdoc and javadoc documentation for Xamarin SDK.')
    parser.add_argument('--mdoc-path', required=True, help='Path to the mdoc XML files')
    parser.add_argument('--javadoc-path', required=True, help='Path to the javadoc HTML files')
    parser.add_argument('--html-template-path', required=True, help='Path to HTML template files')
    parser.add_argument('--output-path', required=True, help='Path to output the merged HTML files')
    parser.add_argument('--version', required=True, help='SDK version number')
    
    args = parser.parse_args()
    
    merger = DocMerger(
        mdoc_path=args.mdoc_path,
        javadoc_path=args.javadoc_path,
        html_template_path=args.html_template_path,
        output_path=args.output_path,
        version=args.version
    )
    
    # Load javadoc content
    merger.load_javadoc_content()
    
    # Process mdoc files
    merger.process_mdoc_files()
    
    logger.info("Documentation merge complete.")

if __name__ == "__main__":
    main()
