"""
HTML report generation for VB6 Project Mapper
"""

import os
import html
from datetime import datetime
import json

from utils.helpers import count_components_by_type, get_dependents
from utils.logger import get_logger
from .diagrams.core_diagram import generate_core_architecture_diagram
from .diagrams.form_diagram import generate_form_relationships_diagram
from .diagrams.class_diagram import generate_business_logic_diagram
from .diagrams.mermaid_script import add_enhanced_mermaid_script

# Initialize module logger
logger = get_logger(__name__)


def generate_html_report(project, output_file):
    """Generate HTML code map report with improved visualization and error handling"""
    logger.info(f"Generating HTML report: {output_file}")

    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.debug(f"Created directory structure for output: {output_dir}")
            except Exception as e:
                logger.error(f"Error creating directory structure: {e}", exc_info=True)
                return False

        with open(output_file, 'w', encoding='utf-8') as f:
            # HTML header with improved CSS
            write_html_header(f, project)

            # Project header
            f.write(f"    <h1>{html.escape(project.name)} - Code Map</h1>\n")
            f.write(f"    <p>Project Path: {html.escape(project.path)}</p>\n")

            # Component count by type
            write_project_summary(f, project)

            # Component legend
            write_component_legend(f)

            # Component list and details section
            write_component_details(f, project)

            # Add complete dependency table
            write_dependency_table(f, project)

            # Add script for table search
            write_table_search_script(f)

            # Generate enhanced visualization diagrams
            generate_enhanced_diagrams(f, project)

            # Add export buttons
            write_export_buttons(f, project)

            # HTML footer
            write_html_footer(f)

        logger.info(f"HTML report generated successfully: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error generating HTML report: {e}", exc_info=True)
        return False


def write_project_summary(f, project):
    """Write the project summary section"""
    f.write("    <h2>Project Summary</h2>\n")
    f.write("    <table>\n")
    f.write("        <tr><th>Component Type</th><th>Count</th></tr>\n")
    f.write(f"        <tr><td>Forms</td><td>{count_components_by_type(project, 'Form')}</td></tr>\n")
    f.write(f"        <tr><td>Modules</td><td>{count_components_by_type(project, 'Module')}</td></tr>\n")
    f.write(f"        <tr><td>Classes</td><td>{count_components_by_type(project, 'Class')}</td></tr>\n")
    f.write(f"        <tr><td>User Controls</td><td>{count_components_by_type(project, 'UserControl')}</td></tr>\n")
    f.write(f"        <tr><td>Property Pages</td><td>{count_components_by_type(project, 'PropertyPage')}</td></tr>\n")
    f.write(f"        <tr><td>Designers</td><td>{count_components_by_type(project, 'Designer')}</td></tr>\n")
    f.write(f"        <tr><th>Total</th><th>{len(project.components)}</th></tr>\n")
    f.write("    </table>\n")


def write_component_legend(f):
    """Write the component type legend"""
    f.write("    <div class='legend'>\n")
    f.write("        <div class='legend-item'><div class='legend-color Form'></div>Form</div>\n")
    f.write("        <div class='legend-item'><div class='legend-color Module'></div>Module</div>\n")
    f.write("        <div class='legend-item'><div class='legend-color Class'></div>Class</div>\n")
    f.write("        <div class='legend-item'><div class='legend-color UserControl'></div>User Control</div>\n")
    f.write("        <div class='legend-item'><div class='legend-color PropertyPage'></div>Property Page</div>\n")
    f.write("        <div class='legend-item'><div class='legend-color Designer'></div>Designer</div>\n")
    f.write("    </div>\n")


def write_component_details(f, project):
    """Write the component list and details section"""
    f.write("    <h2>Project Components</h2>\n")
    f.write("    <div class='container'>\n")

    # Left side - component list with search
    f.write("        <div class='component-list'>\n")
    f.write("            <h3>Components</h3>\n")
    f.write(
        "            <input type='text' id='component-search' class='search-box' placeholder='Search components...' oninput='searchComponents()'>\n")

    for i, component in enumerate(project.components):
        f.write(
            f"            <div class='component {html.escape(component.component_type)}' onclick='showComponentDetails({i})'>"
            f"{html.escape(component.name)} ({html.escape(component.component_type)})</div>\n")

    f.write(
        "            <div id='no-search-results' class='no-results' style='display: none;'>No components found</div>\n")
    f.write("        </div>\n")

    # Right side - component details
    f.write("        <div class='component-details'>\n")
    f.write("            <h3>Component Details</h3>\n")

    for i, component in enumerate(project.components):
        # Component detail section - hidden by default, shown when component is clicked
        display = "" if i == 0 else "style='display:none;'"
        f.write(f"            <div id='component-{i}' class='detail-section' {display}>\n")

        f.write(f"                <h4>{html.escape(component.name)}</h4>\n")
        f.write("                <table>\n")
        f.write(f"                    <tr><td>Type:</td><td>{html.escape(component.component_type)}</td></tr>\n")
        f.write(f"                    <tr><td>File:</td><td>{html.escape(component.filename)}</td></tr>\n")
        f.write("                </table>\n")

        # Dependencies
        f.write("                <h5>Dependencies:</h5>\n")
        if component.dependencies:
            f.write("                <ul>\n")
            for dep in sorted(set(component.dependencies)):  # Use set to remove duplicates
                f.write(f"                    <li>{html.escape(dep)}</li>\n")
            f.write("                </ul>\n")
        else:
            f.write("                <p>No dependencies found</p>\n")

        # Dependents (components that depend on this one)
        f.write("                <h5>Referenced by:</h5>\n")
        dependents = get_dependents(project, component)
        if dependents:
            f.write("                <ul>\n")
            for dep in sorted(dependents, key=lambda x: x.name):  # Sort by name
                f.write(f"                    <li>{html.escape(dep.name)}</li>\n")
            f.write("                </ul>\n")
        else:
            f.write("                <p>Not referenced by any component</p>\n")

        f.write("            </div>\n")

    f.write("        </div>\n")
    f.write("    </div>\n")


def write_dependency_table(f, project):
    """Write the dependency table section"""
    f.write("    <div class='dependency-graph'>\n")
    f.write("        <h2>Dependency Table</h2>\n")
    f.write(
        "        <input type='text' id='table-search' class='search-box' placeholder='Search dependency table...' oninput='searchTable()'>\n")
    f.write("        <table id='dependency-table'>\n")
    f.write("            <tr><th>Component</th><th>Type</th><th>Dependencies</th><th>Referenced By</th></tr>\n")

    for component in sorted(project.components, key=lambda x: x.name):  # Sort by name
        f.write("            <tr>\n")
        f.write(f"                <td>{html.escape(component.name)}</td>\n")
        f.write(f"                <td>{html.escape(component.component_type)}</td>\n")

        # Dependencies
        f.write("                <td>\n")
        if component.dependencies:
            f.write(", ".join(html.escape(dep) for dep in sorted(set(component.dependencies))))
        else:
            f.write("None")
        f.write("</td>\n")

        # Referenced by
        f.write("                <td>\n")
        dependents = get_dependents(project, component)
        if dependents:
            f.write(", ".join(html.escape(dep.name) for dep in sorted(dependents, key=lambda x: x.name)))
        else:
            f.write("None")
        f.write("</td>\n")
        f.write("            </tr>\n")

    f.write("        </table>\n")
    f.write("    </div>\n")


def write_table_search_script(f):
    """Write the JavaScript for table search functionality"""
    f.write("""
    <script>
        function searchTable() {
            const searchTerm = document.getElementById('table-search').value.toLowerCase();
            const table = document.getElementById('dependency-table');
            const rows = table.getElementsByTagName('tr');

            // Skip header row
            for (let i = 1; i < rows.length; i++) {
                const rowText = rows[i].textContent.toLowerCase();
                if (rowText.includes(searchTerm)) {
                    rows[i].style.display = '';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        }
    </script>
    """)


def generate_enhanced_diagrams(f, project):
    """Generate multiple specialized diagram views for complex projects"""

    # Add tabbed interface for multiple diagram views
    f.write("""
    <div class='dependency-graph'>
        <h2>Visual Dependency Diagrams</h2>
        <p>Select different views to explore the project architecture:</p>

        <div class="diagram-tabs">
            <button class="tab-button active" onclick="switchTab('core-architecture')">Core Architecture</button>
            <button class="tab-button" onclick="switchTab('form-relationships')">Form Relationships</button>
            <button class="tab-button" onclick="switchTab('business-logic')">Business Logic</button>
            <button class="tab-button" onclick="switchTab('focus-mode')">Focus Mode</button>
        </div>

        <div class="tab-content" id="core-architecture" style="display: block;">
            <h3>Core Architecture View</h3>
            <p>This diagram shows the 20 most connected components in the project.</p>
            <div class="filter-controls">
                <button id="core-expand-all" class="control-button">Expand All</button>
                <button id="core-collapse-all" class="control-button">Collapse All</button>
            </div>
            <div id="core-diagram" class="mermaid">
    """)

    # Generate core architecture diagram (top 20 most connected components)
    generate_core_architecture_diagram(f, project)
    f.write("</div>\n        </div>\n")

    # Form relationships tab
    f.write("""
        <div class="tab-content" id="form-relationships" style="display: none;">
            <h3>Form Relationships View</h3>
            <p>This diagram shows only the relationships between forms.</p>
            <div class="filter-controls">
                <input type="text" id="form-search" placeholder="Search forms..." class="search-control">
                <button id="form-apply-search" class="control-button">Filter</button>
            </div>
            <div id="form-diagram" class="mermaid">
    """)

    # Generate form-to-form diagram
    generate_form_relationships_diagram(f, project)
    f.write("</div>\n        </div>\n")

    # Business logic tab
    f.write("""
        <div class="tab-content" id="business-logic" style="display: none;">
            <h3>Business Logic View</h3>
            <p>This diagram shows classes and their key dependencies.</p>
            <div id="business-diagram" class="mermaid">
    """)

    # Generate business logic diagram
    generate_business_logic_diagram(f, project)
    f.write("</div>\n        </div>\n")

    # Simplified Focus mode tab - No more Mermaid diagram
    f.write("""
        <div class="tab-content" id="focus-mode" style="display: none;">
            <h3>Focus Mode</h3>
            <p>Explore the direct dependencies of a selected component.</p>
            <div class="filter-controls" style="margin-bottom: 15px;">
                <select id="focus-component" class="component-select" style="padding: 8px; min-width: 250px; margin-right: 10px;">
                    <option value="">Select a component...</option>
    """)

    # Add all components to the dropdown
    for component in sorted(project.components, key=lambda x: x.name):
        f.write(
            f'                    <option value="{html.escape(component.name)}">{html.escape(component.name)} ({html.escape(component.component_type)})</option>\n')

    f.write("""
                </select>
                <label class="depth-control" style="margin-right: 10px;">
                    <span>Depth:</span>
                    <select id="focus-depth">
                        <option value="1">1 level</option>
                        <option value="2" selected>2 levels</option>
                        <option value="3">3 levels</option>
                    </select>
                </label>
                <button id="focus-generate" class="control-button" style="padding: 8px 16px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Generate
                </button>
            </div>

            <!-- Simple container for the dynamically generated HTML tables -->
            <div id="focus-diagram">
                <div style="padding: 20px; text-align: center; background-color: #f5f5f5; border-radius: 4px;">
                    Select a component and click Generate to view its dependencies
                </div>
            </div>
        </div>
    </div>
    """)

    # Add JavaScript for tab switching and interactive diagrams
    add_visualization_scripts(f, project)

    # Add Mermaid script loading and initialization
    add_enhanced_mermaid_script(f)


def write_export_buttons(f, project):
    """Write export buttons for diagrams"""
    f.write("""
    <div style="margin-top: 30px; text-align: center;">
        <button id="exportSVG" class="button" style="margin-right: 10px;">Export Diagram as SVG</button>
        <button id="exportPNG" class="button" style="background-color: #2ecc71;">Export Diagram as PNG</button>
    </div>

    <script>
        document.getElementById('exportSVG').addEventListener('click', function() {
            // Find the active tab's diagram
            const activeTab = document.querySelector('.tab-content[style*="display: block"]');
            const svgElement = activeTab.querySelector('svg');
            if (!svgElement) {
                alert('No SVG diagram found to export');
                return;
            }

            // Create a copy of the SVG to manipulate for export
            const svgCopy = svgElement.cloneNode(true);
            const svgData = new XMLSerializer().serializeToString(svgCopy);
            const blob = new Blob([svgData], {type: 'image/svg+xml'});
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = '""" + html.escape(project.name) + """_dependency_diagram.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });

        document.getElementById('exportPNG').addEventListener('click', function() {
            // Find the active tab's diagram
            const activeTab = document.querySelector('.tab-content[style*="display: block"]');
            const svgElement = activeTab.querySelector('svg');
            if (!svgElement) {
                alert('No SVG diagram found to export');
                return;
            }

            // Create a canvas and draw the SVG on it
            const canvas = document.createElement('canvas');
            const svgRect = svgElement.getBoundingClientRect();
            canvas.width = svgRect.width;
            canvas.height = svgRect.height;
            const ctx = canvas.getContext('2d');

            // Create an image from the SVG
            const img = new Image();
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const url = URL.createObjectURL(svgBlob);

            img.onload = function() {
                ctx.drawImage(img, 0, 0);
                URL.revokeObjectURL(url);

                // Convert canvas to PNG
                try {
                    const pngUrl = canvas.toDataURL('image/png');
                    const a = document.createElement('a');
                    a.href = pngUrl;
                    a.download = '""" + html.escape(project.name) + """_dependency_diagram.png';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                } catch(e) {
                    alert('Failed to export as PNG. This may be due to CORS restrictions with external SVG content.');
                    console.error(e);
                }
            };

            img.src = url;
        });
    </script>
    """)


def write_html_footer(f):
    """Write the HTML footer"""
    f.write(f"""
    <footer>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>VB6 Project Mapper - A tool for analyzing Visual Basic 6.0 projects</p>
    </footer>
</body>
</html>
    """)


def add_visualization_scripts(f, project):
    """Add JavaScript for the enhanced visualization features"""
    # Build simplified project data
    project_data = {"components": {}}

    for comp in project.components:
        # Get dependents
        dependents = [dep.name for dep in get_dependents(project, comp)]

        # Add component data - use a sanitized version of the name for the key to avoid XSS
        safe_name = comp.name
        project_data["components"][safe_name] = {
            "type": comp.component_type,
            "dependencies": list(set(comp.dependencies)),
            "dependents": dependents
        }

    # Use json.dumps with ensure_ascii=False to properly escape special characters
    import json
    safe_project_data = json.dumps(project_data, ensure_ascii=False)

    # Ensure all component names are properly HTML-escaped in JavaScript
    # by replacing potential script tags with escaped versions
    safe_project_data = safe_project_data.replace("<script>", "&lt;script&gt;")
    safe_project_data = safe_project_data.replace("</script>", "&lt;/script&gt;")

    # Add scripts for tab switching and interactive diagrams
    f.write(f"""
    <script>
        // Store project data for use in dynamic diagrams
        const projectData = {safe_project_data};

        // Tab switching functionality
        function switchTab(tabId) {{
            // Hide all tab contents
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {{
                tabContents[i].style.display = 'none';
            }}

            // Deactivate all tab buttons
            const tabButtons = document.getElementsByClassName('tab-button');
            for (let i = 0; i < tabButtons.length; i++) {{
                tabButtons[i].classList.remove('active');
            }}

            // Show selected tab content and activate button
            document.getElementById(tabId).style.display = 'block';

            // Find and activate the clicked button
            for (let i = 0; i < tabButtons.length; i++) {{
                if (tabButtons[i].getAttribute('onclick').includes(tabId)) {{
                    tabButtons[i].classList.add('active');
                }}
            }}
        }}

        // Wait for page load
        window.addEventListener('load', function() {{
            // Initialize Focus Mode
            document.getElementById('focus-generate').addEventListener('click', function() {{
                generateFocusDiagram();
            }});

            // Form search functionality
            document.getElementById('form-apply-search').addEventListener('click', function() {{
                const searchTerm = document.getElementById('form-search').value.toLowerCase();
                filterFormDiagram(searchTerm);
            }});

            // Core diagram expand/collapse
            document.getElementById('core-expand-all').addEventListener('click', function() {{
                expandAllNodes('core-diagram');
            }});

            document.getElementById('core-collapse-all').addEventListener('click', function() {{
                collapseAllNodes('core-diagram');
            }});
        }});

        // Function to escape HTML for safe insertion
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // Modified function that uses dynamic tables instead of Mermaid diagrams
        function generateFocusDiagram() {{
            const componentName = document.getElementById('focus-component').value;
            const depth = parseInt(document.getElementById('focus-depth').value);
            const diagramElement = document.getElementById('focus-diagram');

            // Show loading message
            diagramElement.innerHTML = '<div style="padding: 20px; text-align: center;">Generating diagram...</div>';

            if (!componentName) {{
                diagramElement.innerHTML = '<div class="error-message">Please select a component first</div>';
                return;
            }}

            // Create a simple HTML table showing dependencies instead of trying to render with Mermaid
            let tableHTML = `<h4>Direct Dependencies for: ${{escapeHtml(componentName)}}</h4>`;

            // Get component information
            const component = projectData.components[componentName];
            if (!component) {{
                diagramElement.innerHTML = '<div class="error-message">Component data not found</div>';
                return;
            }}

            // Add dependencies table
            if (component.dependencies && component.dependencies.length > 0) {{
                tableHTML += `<h5>Dependencies (${{component.dependencies.length}}):</h5>`;
                tableHTML += '<table class="dependency-table" style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">';
                tableHTML += '<tr><th style="text-align: left; padding: 8px; border: 1px solid #ddd; background-color: #f5f5f5;">Component</th><th style="text-align: left; padding: 8px; border: 1px solid #ddd; background-color: #f5f5f5;">Type</th></tr>';

                component.dependencies.forEach(dep => {{
                    const depComponent = projectData.components[dep];
                    const type = depComponent ? depComponent.type : "Unknown";
                    const typeClass = type.toLowerCase() === "class" ? "cls" : type.toLowerCase();

                    tableHTML += `<tr>`;
                    tableHTML += `<td style="padding: 8px; border: 1px solid #ddd;"><span class="component ${{typeClass}}" style="padding: 2px 5px; border-radius: 3px;">${{escapeHtml(dep)}}</span></td>`;
                    tableHTML += `<td style="padding: 8px; border: 1px solid #ddd;">${{escapeHtml(type)}}</td>`;
                    tableHTML += `</tr>`;
                }});

                tableHTML += '</table>';
            }} else {{
                tableHTML += '<p>This component has no dependencies.</p>';
            }}

            // Add dependents table
            if (component.dependents && component.dependents.length > 0) {{
                tableHTML += `<h5>Referenced By (${{component.dependents.length}}):</h5>`;
                tableHTML += '<table class="dependency-table" style="width: 100%; border-collapse: collapse;">';
                tableHTML += '<tr><th style="text-align: left; padding: 8px; border: 1px solid #ddd; background-color: #f5f5f5;">Component</th><th style="text-align: left; padding: 8px; border: 1px solid #ddd; background-color: #f5f5f5;">Type</th></tr>';

                component.dependents.forEach(dep => {{
                    const depComponent = projectData.components[dep];
                    const type = depComponent ? depComponent.type : "Unknown";
                    const typeClass = type.toLowerCase() === "class" ? "cls" : type.toLowerCase();

                    tableHTML += `<tr>`;
                    tableHTML += `<td style="padding: 8px; border: 1px solid #ddd;"><span class="component ${{typeClass}}" style="padding: 2px 5px; border-radius: 3px;">${{escapeHtml(dep)}}</span></td>`;
                    tableHTML += `<td style="padding: 8px; border: 1px solid #ddd;">${{escapeHtml(type)}}</td>`;
                    tableHTML += `</tr>`;
                }});

                tableHTML += '</table>';
            }} else {{
                tableHTML += '<p>This component is not referenced by any other component.</p>';
            }}

            // Set the HTML content
            diagramElement.innerHTML = tableHTML;

            // Display a message about Mermaid diagrams
            const infoMessage = document.createElement('div');
            infoMessage.style.marginTop = '20px';
            infoMessage.style.padding = '10px';
            infoMessage.style.backgroundColor = '#f8f9fa';
            infoMessage.style.border = '1px solid #ddd';
            infoMessage.style.borderRadius = '4px';
            infoMessage.innerHTML = '<p><strong>Note:</strong> Mermaid diagram generation is currently under maintenance. We are showing tabular dependency information instead.</p>';
            diagramElement.appendChild(infoMessage);
        }}

        // Filter form diagram based on search term
        function filterFormDiagram(searchTerm) {{
            // Implementation would filter and redraw the form diagram
            console.log("Filtering forms by:", searchTerm);
            // For now, just show a message - actual implementation would redraw the diagram
            alert("Form filtering is being implemented. Search term: " + searchTerm);
        }}

        // Expand all nodes in a diagram
        function expandAllNodes(diagramId) {{
            // Implementation would expand all collapsible nodes
            console.log("Expanding all nodes in", diagramId);
            // For now, just show a message - actual implementation would interact with Mermaid API
            alert("Node expansion is being implemented for " + diagramId);
        }}

        // Collapse all nodes in a diagram
        function collapseAllNodes(diagramId) {{
            // Implementation would collapse all expanded nodes
            console.log("Collapsing all nodes in", diagramId);
            // For now, just show a message - actual implementation would interact with Mermaid API
            alert("Node collapsing is being implemented for " + diagramId);
        }}
    </script>
    """)


def write_html_header(f, project):
    """Write the HTML header section with CSS styles"""
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{html.escape(project.name)} - Code Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            line-height: 1.6; 
            color: #333;
            background-color: #f9f9f9;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
        h2 {{ color: #3498db; margin-top: 30px; }}
        h3 {{ color: #2980b9; }}
        h4 {{ color: #16a085; }}
        h5 {{ color: #27ae60; margin-top: 15px; margin-bottom: 5px; }}
        .container {{ display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px; }}
        .component-list {{ 
            width: 300px; 
            background: #fff; 
            padding: 15px; 
            border-radius: 5px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-height: 80vh;
            overflow-y: auto;
        }}
        .component-details {{ 
            flex: 1; 
            min-width: 300px; 
            background: #fff; 
            padding: 15px; 
            border-radius: 5px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-height: 80vh;
            overflow-y: auto;
        }}
        .component {{ 
            margin-bottom: 8px; 
            cursor: pointer; 
            padding: 8px; 
            border-radius: 4px; 
            transition: all 0.2s;
        }}
        .component:hover {{ 
            transform: translateX(5px);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .component.active {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }}
        .Form {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; }}
        .Module {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; }}
        .Class {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
        .UserControl {{ background-color: #f3e5f5; border-left: 4px solid #9c27b0; }}
        .PropertyPage {{ background-color: #fffde7; border-left: 4px solid #ffc107; }}
        .Designer {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 15px 0; 
            background-color: #fff;
        }}
        th, td {{ border: 1px solid #e1e1e1; padding: 10px; text-align: left; }}
        th {{ background-color: #f5f5f5; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .dependency-graph {{ 
            margin-top: 40px; 
            border: 1px solid #e1e1e1; 
            padding: 20px; 
            border-radius: 5px; 
            background: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
        .legend-item {{ display: flex; align-items: center; margin-right: 15px; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 8px; border-radius: 3px; }}
        .mermaid {{ 
            overflow: auto; 
            max-width: 100%; 
            min-height: 300px;
            position: relative;
        }}
        footer {{ 
            margin-top: 50px; 
            text-align: center; 
            color: #7f8c8d; 
            font-size: 0.9em; 
            padding-top: 20px; 
            border-top: 1px solid #ecf0f1; 
        }}
        .search-box {{
            margin-bottom: 15px;
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .no-results {{
            color: #999;
            font-style: italic;
            padding: 10px;
        }}
        .button {{
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: #2980b9;
        }}
        @media (max-width: 768px) {{
            .container {{ flex-direction: column; }}
            .component-list, .component-details {{ width: 100%; }}
        }}

        /* Styles for enhanced visualization */
        .diagram-tabs {{
            display: flex;
            border-bottom: 1px solid #ccc;
            margin-bottom: 20px;
            overflow-x: auto;
        }}

        .tab-button {{
            padding: 10px 20px;
            background: #f5f5f5;
            border: none;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
            cursor: pointer;
            font-weight: normal;
            white-space: nowrap;
        }}

        .tab-button.active {{
            background: #2196f3;
            color: white;
            font-weight: bold;
        }}

        .tab-content {{
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }}

        .filter-controls {{
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .search-control {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            min-width: 250px;
        }}

        .component-select {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            min-width: 300px;
        }}

        .control-button {{
            padding: 8px 16px;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}

        .control-button:hover {{
            background: #0d8aee;
        }}

        .depth-control {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .depth-control select {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}

        .error-message {{
            padding: 15px;
            background: #ffebee;
            border: 1px solid #f44336;
            border-radius: 4px;
            color: #d32f2f;
            margin-top: 15px;
        }}

        /* Improved diagram controls positioning and styling */
        .diagram-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 5px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            z-index: 100;
            display: flex;
            gap: 5px;
        }}

        .diagram-controls button {{
            padding: 5px 10px;
            border: 1px solid #ccc;
            background: white;
            border-radius: 3px;
            cursor: pointer;
        }}

        .diagram-controls button:hover {{
            background: #f5f5f5;
        }}
    </style>
    <script>
        function showComponentDetails(index) {{
            // Update active class
            const components = document.getElementsByClassName('component');
            for (let i = 0; i < components.length; i++) {{
                components[i].classList.remove('active');
            }}
            components[index].classList.add('active');

            // Show selected component details
            const details = document.getElementsByClassName('detail-section');
            for (let i = 0; i < details.length; i++) {{
                details[i].style.display = 'none';
            }}
            document.getElementById('component-' + index).style.display = 'block';
        }}

        function searchComponents() {{
            const searchTerm = document.getElementById('component-search').value.toLowerCase();
            const components = document.getElementsByClassName('component');
            let visibleCount = 0;

            for (let i = 0; i < components.length; i++) {{
                const componentText = components[i].textContent.toLowerCase();
                if (componentText.includes(searchTerm)) {{
                    components[i].style.display = '';
                    visibleCount++;
                }} else {{
                    components[i].style.display = 'none';
                }}
            }}

            // Show no results message if needed
            const noResults = document.getElementById('no-search-results');
            if (visibleCount === 0) {{
                noResults.style.display = 'block';
            }} else {{
                noResults.style.display = 'none';
            }}
        }}
    </script>
</head>
<body>
""")
