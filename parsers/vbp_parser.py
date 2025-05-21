"""
VB6 Project File Parser for VB6 Project Mapper
Handles parsing of VBP files to extract project information and components
"""

import os
import logging
from models.components import VB6Project
from utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


def parse_vbp_file(vbp_file_path):
    """
    Parse a VB6 project file and extract project information

    Args:
        vbp_file_path (str): Path to the VB6 project file (.vbp)

    Returns:
        VB6Project: Project object with extracted information, or None if parsing failed
    """
    logger.info(f"Parsing VB6 project file: {vbp_file_path}")

    project = VB6Project()
    project.filename = os.path.basename(vbp_file_path)
    project.path = os.path.dirname(vbp_file_path)

    if not os.path.exists(vbp_file_path):
        logger.error(f"Project file does not exist: {vbp_file_path}")
        return None

    try:
        logger.debug(f"Opening project file: {vbp_file_path}")
        with open(vbp_file_path, 'r', encoding='latin-1') as file:
            line_count = 0
            component_counts = {
                'Form': 0,
                'Module': 0,
                'Class': 0,
                'UserControl': 0,
                'PropertyPage': 0,
                'Designer': 0
            }

            for line in file:
                line_count += 1
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                try:
                    # Extract project name
                    if line.startswith('Name='):
                        name_value = line[5:].strip()
                        # Remove surrounding quotes if present
                        if (name_value.startswith('"') and name_value.endswith('"')) or \
                                (name_value.startswith("'") and name_value.endswith("'")):
                            name_value = name_value[1:-1]
                        project.name = name_value
                        logger.info(f"Found project name: {project.name}")
                        continue

                    # Process forms
                    if line.startswith('Form='):
                        result = add_component_from_line(project, line[5:], 'Form')
                        if result:
                            component_counts['Form'] += 1
                        continue

                    # Process modules
                    if line.startswith('Module='):
                        result = add_component_from_line(project, line[7:], 'Module')
                        if result:
                            component_counts['Module'] += 1
                        continue

                    # Process class modules
                    if line.startswith('Class='):
                        result = add_component_from_line(project, line[6:], 'Class')
                        if result:
                            component_counts['Class'] += 1
                        continue

                    # Process user controls
                    if line.startswith('UserControl='):
                        result = add_component_from_line(project, line[12:], 'UserControl')
                        if result:
                            component_counts['UserControl'] += 1
                        continue

                    # Process property pages
                    if line.startswith('PropertyPage='):
                        result = add_component_from_line(project, line[13:], 'PropertyPage')
                        if result:
                            component_counts['PropertyPage'] += 1
                        continue

                    # Process designers
                    if line.startswith('Designer='):
                        result = add_component_from_line(project, line[9:], 'Designer')
                        if result:
                            component_counts['Designer'] += 1
                        continue

                    # Process references (optional)
                    if line.startswith('Reference='):
                        # Could extract references to external libraries here
                        logger.debug(f"Found reference: {line[10:]}")
                        continue

                except Exception as e:
                    logger.warning(f"Error processing line {line_count}: {line}", exc_info=True)
                    continue

            # Log component stats
            logger.info(f"VB6 project parsed successfully: {project.name}")
            logger.info(f"Project contains {len(project.components)} components")

            for comp_type, count in component_counts.items():
                if count > 0:
                    logger.info(f"  - {comp_type}s: {count}")

            if not project.name:
                logger.warning("Project name not found in VBP file")

            if not project.components:
                logger.warning("No components found in VBP file")

            return project

    except UnicodeDecodeError as e:
        logger.error(f"Character encoding error: {e}", exc_info=True)
        logger.error("VBP file contains characters that couldn't be decoded with Latin-1 encoding")
        return None
    except Exception as e:
        logger.error(f"Error parsing VBP file: {e}", exc_info=True)
        return None


def add_component_from_line(project, file_info, component_type):
    """
    Parse component information from a line in the VBP file

    Args:
        project (VB6Project): The project to add the component to
        file_info (str): The component information from the VBP file
        component_type (str): The type of component

    Returns:
        bool: True if component was added successfully, False otherwise
    """
    try:
        parts = file_info.split(';')

        if len(parts) >= 1:
            filename = parts[0].strip()

            # Try to extract component name from the parts
            component_name = os.path.splitext(os.path.basename(filename))[0]
            for part in parts[1:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    if key.strip() == "":
                        # Remove quotes if present
                        value = value.strip()
                        if (value.startswith('"') and value.endswith('"')) or \
                                (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        component_name = value
                        break

            # Check if component with this name already exists
            exists = project.find_component_by_name(component_name)
            if exists:
                logger.warning(f"Duplicate component name found: {component_name} - {component_type}")
                # Make name unique by appending a counter
                counter = 1
                while project.find_component_by_name(f"{component_name}_{counter}"):
                    counter += 1
                component_name = f"{component_name}_{counter}"
                logger.warning(f"Renamed to: {component_name}")

            # Add component to project
            project.add_component(component_name, filename, component_type)
            logger.debug(f"Added component: {component_name} ({component_type})")
            return True

        else:
            logger.warning(f"Invalid component format: {file_info}")
            return False

    except Exception as e:
        logger.error(f"Error adding component from line: {file_info}", exc_info=True)
        logger.error(f"Exception: {e}", exc_info=True)
        return False