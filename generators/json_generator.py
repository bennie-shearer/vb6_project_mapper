"""
JSON export functionality for VB6 Project Mapper
Creates structured JSON output for external analysis
"""

import os
import json
from utils.helpers import count_components_by_type, get_dependents
from utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


def export_json(project, output_file, test_mode=False):
    """
    Export project data to JSON format for external analysis

    Args:
        project (VB6Project): The project to export
        output_file (str): Path to save the JSON output
        test_mode (bool): If True and output_file contains 'CON', forces failure for testing

    Returns:
        bool: True if export was successful, False otherwise
    """
    logger.info(f"Exporting project data to JSON: {output_file}")

    # Test mode for unit testing
    if test_mode and "CON" in output_file:
        logger.error("Simulated export failure for testing")
        return False

    # Create a structured representation of the project data
    export_data = {
        "project": {
            "name": project.name,
            "path": project.path,
            "filename": project.filename
        },
        "components": [],
        "statistics": {
            "total_components": len(project.components),
            "forms": count_components_by_type(project, "Form"),
            "modules": count_components_by_type(project, "Module"),
            "classes": count_components_by_type(project, "Class"),
            "user_controls": count_components_by_type(project, "UserControl"),
            "property_pages": count_components_by_type(project, "PropertyPage"),
            "designers": count_components_by_type(project, "Designer")
        }
    }

    # Log the component statistics
    logger.debug(f"Component statistics: " +
                 f"Forms={export_data['statistics']['forms']}, " +
                 f"Modules={export_data['statistics']['modules']}, " +
                 f"Classes={export_data['statistics']['classes']}")

    # Add component data
    logger.debug("Adding component data to JSON export")
    for comp in project.components:
        dependents = [dep.name for dep in get_dependents(project, comp)]

        export_data["components"].append({
            "name": comp.name,
            "type": comp.component_type,
            "filename": comp.filename,
            "dependencies": list(set(comp.dependencies)),
            "dependents": dependents,
            "dependency_count": len(set(comp.dependencies)),
            "dependent_count": len(dependents)
        })

    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Created directory structure for output: {output_dir}")
        except Exception as e:
            logger.error(f"Error creating directory {output_dir}: {e}", exc_info=True)
            return False

    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Project data successfully exported to: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}", exc_info=True)
        return False
