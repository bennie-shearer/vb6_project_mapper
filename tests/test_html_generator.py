import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
import re

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.components import VB6Project, VB6Component
from generators.html_generator import generate_html_report


class TestHTMLGenerator(unittest.TestCase):
    """Test cases for the HTML report generator"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_report.html")

        # Create a test project
        self.project = VB6Project()
        self.project.name = "TestProject"
        self.project.path = self.temp_dir
        self.project.filename = "TestProject.vbp"

        # Add test components
        self.form1 = self.project.add_component("frmMain", "frmMain.frm", "Form")
        self.form2 = self.project.add_component("frmOptions", "frmOptions.frm", "Form")
        self.module1 = self.project.add_component("modUtils", "modUtils.bas", "Module")
        self.class1 = self.project.add_component("clsData", "clsData.cls", "Class")

        # Add dependencies
        self.form1.dependencies = ["frmOptions", "modUtils", "clsData"]
        self.form2.dependencies = ["modUtils", "frmMain"]
        self.module1.dependencies = ["clsData"]
        self.class1.dependencies = []

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_generate_html_report(self):
        """Test that HTML report is generated successfully"""
        # Generate the report
        result = generate_html_report(self.project, self.output_file)

        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file))

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that the report contains essential elements
        self.assertIn("<title>TestProject - Code Map</title>", content)
        self.assertIn("<h1>TestProject - Code Map</h1>", content)
        self.assertIn("<h2>Project Summary</h2>", content)

        # Check for component counts
        self.assertIn("<tr><td>Forms</td><td>2</td></tr>", content)
        self.assertIn("<tr><td>Modules</td><td>1</td></tr>", content)
        self.assertIn("<tr><td>Classes</td><td>1</td></tr>", content)

        # Check for component listings
        self.assertIn("frmMain", content)
        self.assertIn("frmOptions", content)
        self.assertIn("modUtils", content)
        self.assertIn("clsData", content)

        # Check for dependency information
        self.assertIn("Dependencies", content)
        self.assertIn("Referenced by", content)

    def test_html_escaping(self):
        """Test that HTML content is properly escaped"""
        # Create a component with HTML in the name
        component = self.project.add_component("<script>alert('XSS')</script>", "malicious.frm", "Form")

        # Generate the report
        generate_html_report(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that HTML was escaped
        self.assertIn("&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;", content)
        self.assertNotIn("<script>alert('XSS')</script>", content)

    def test_diagram_generation(self):
        """Test that diagrams are included in the report"""
        # Generate the report
        generate_html_report(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for diagram related content
        self.assertIn("Visual Dependency Diagrams", content)
        self.assertIn("Core Architecture View", content)
        self.assertIn("Form Relationships View", content)
        self.assertIn("Business Logic View", content)

        # Check for Mermaid diagram content
        self.assertIn("class=\"mermaid\"", content)
        self.assertIn("graph LR", content)  # Mermaid syntax

    def test_interactive_features(self):
        """Test that interactive features are included"""
        # Generate the report
        generate_html_report(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for search functionality
        self.assertIn("search-box", content)
        self.assertIn("searchComponents()", content)
        self.assertIn("searchTable()", content)

        # Check for tab switching functionality
        self.assertIn("switchTab(", content)

        # Check for export buttons
        self.assertIn("Export Diagram as SVG", content)
        self.assertIn("Export Diagram as PNG", content)

    def test_error_handling(self):
        """Test HTML generation with invalid input"""
        # Create a mock open function that raises an exception
        original_open = open

        def mock_open(*args, **kwargs):
            if args[0] == self.output_file:
                raise IOError("Mocked file opening error")
            return original_open(*args, **kwargs)

        # Replace built-in open with our mock
        import builtins
        builtins.open = mock_open

        try:
            # This should now fail because we're mocking an IOError
            result = generate_html_report(self.project, self.output_file)
            self.assertFalse(result)
        finally:
            # Restore the original open function
            builtins.open = original_open

    def test_component_details(self):
        """Test that component details are properly displayed"""
        # Generate the report
        generate_html_report(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that required information is present
        self.assertIn("frmMain", content)
        self.assertIn("Form", content)
        self.assertIn("Dependencies", content)

        # Verify dependencies
        for dep in self.form1.dependencies:
            self.assertIn(dep, content)


if __name__ == '__main__':
    unittest.main()