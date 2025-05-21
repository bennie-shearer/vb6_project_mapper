#!/usr/bin/env python3
"""
VB6 Project Mapper - Utility to generate a code map from a VB6 project file
Enhanced Version with Advanced Visualization Features and Logging
"""

import os
import sys
import argparse
import logging
from datetime import datetime

from utils.logger import setup_logging, get_run_id
from parsers.vbp_parser import parse_vbp_file
from analyzers.dependency_analyzer import analyze_dependencies
from generators.html_generator import generate_html_report
from generators.json_generator import export_json


def main():
    # Parse command line arguments first (before setting up logging)
    parser = argparse.ArgumentParser(description="Generate a code map from a VB6 project file")
    parser.add_argument("vbp_file", help="Path to the VB6 project file (.vbp)")
    parser.add_argument("-o", "--output", help="Output file name (default: [project_name]_CodeMap.html)")
    parser.add_argument("-j", "--json", action="store_true", help="Also export as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress console output except errors")
    args = parser.parse_args()

    # Determine console log level based on arguments
    console_level = logging.INFO  # Default
    if args.verbose:
        console_level = logging.DEBUG
    elif args.quiet:
        console_level = logging.ERROR

    # Initialize logger with possible command-line override
    logger = setup_logging('main', console_level=console_level)

    # Get run ID for this session
    run_id = get_run_id()
    logger.info(f"Starting VB6 Project Mapper (Run ID: {run_id})")

    # Check if file exists
    if not os.path.exists(args.vbp_file):
        logger.critical(f"Project file not found: {args.vbp_file}")
        return 1

    # Display banner information
    print_banner(logger)

    # Parse VBP file
    logger.info(f"Parsing VB6 project file: {args.vbp_file}")
    project = parse_vbp_file(args.vbp_file)
    if not project:
        logger.critical("Failed to parse the project file")
        return 1

    logger.info(f"Successfully parsed project '{project.name}' with {len(project.components)} components")
    logger.debug(f"Component breakdown: Forms={count_by_type(project, 'Form')}, " +
                 f"Modules={count_by_type(project, 'Module')}, " +
                 f"Classes={count_by_type(project, 'Class')}")

    # Analyze dependencies
    logger.info("Starting dependency analysis")
    analyze_dependencies(project)

    dependency_count = sum(len(c.dependencies) for c in project.components)
    logger.info(f"Dependency analysis complete. Found {dependency_count} total dependencies")

    # Generate output filename if not specified
    if not args.output:
        output_file = os.path.join(project.path, f"{project.name}_CodeMap.html")
    else:
        output_file = args.output

    logger.info(f"Output file will be: {output_file}")

    # Generate HTML report
    logger.info("Generating HTML report")
    try:
        generate_html_report(project, output_file)
        logger.info(f"Code map has been generated: {output_file}")
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}", exc_info=True)
        return 1

    # Export as JSON if requested
    if args.json:
        logger.info("Exporting JSON data")
        json_file = os.path.splitext(output_file)[0] + ".json"
        try:
            export_json(project, json_file)
            logger.info(f"JSON data has been exported: {json_file}")
        except Exception as e:
            logger.error(f"Error exporting JSON data: {e}", exc_info=True)
            return 1

    logger.info("VB6 Project Mapper completed successfully")
    return 0


def count_by_type(project, component_type):
    """Count components by type"""
    return sum(1 for component in project.components if component.component_type == component_type)


def print_banner(logger):
    try:
    # Print the application banner
        logger.info(f"**************************************************************************")
        logger.info(f"*                                                                        *")
        logger.info(f"*   VB6 Project Mapper                                                   *")
        logger.info(f"*      A Python utility for analyzing and visualizing Visual Basic 6.0   *")
        logger.info(f"*      project structure and dependencies.                               *")
        logger.info(f"*                                                                        *")
        logger.info(f"*   Developed by Bennie Shearer (Retired)                                *")
        logger.info(f"*   - Inspired by the need to assist developers working with             *")
        logger.info(f"*     legacy VB6 applications                                            *")
        logger.info(f"*                                                                        *")
        logger.info(f"*   License                                                              *")
        logger.info(f"*   - This project is licensed under the MIT License                     *")
        logger.info(f"*     see the LICENSE file for details                                   *")
        logger.info(f"*                                                                        *")
        logger.info(f"*   Acknowledgments                                                      *")
        logger.info(f"*   - Thanks to all my mentors and contributors                          *")
        logger.info(f"*   - Special thanks to:                                                 *")
        logger.info(f"*     * Mermaid.js Project          https://mermaid.js.org/              *")
        logger.info(f"*     * PyCharm by JetBrains s.r.o. https://www.jetbrains.com/pycharm/   *")
        logger.info(f"*     * Claude by Anthropic PBC     https://www.anthropic.com/           *")
        logger.info(f"*                                                                        *")
        logger.info(f"*-************************************************************************")
    except Exception as e:
        logger.error(f'Error print_banner()')
        return 1

if __name__ == "__main__":
    # Wrap everything in try-except to catch unexpected errors
    try:
        sys.exit(main())
    except Exception as e:
        # Set up a basic logger for critical errors if normal logging isn't working
        logger = logging.getLogger("error_handler")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("CRITICAL ERROR: %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.CRITICAL)

        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)