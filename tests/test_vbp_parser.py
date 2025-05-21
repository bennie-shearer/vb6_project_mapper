import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.vbp_parser import parse_vbp_file
from models.components import VB6Project


class TestVBPParser(unittest.TestCase):
    """Test cases for the VB6 project file parser"""

    def setUp(self):
        """Set up test paths"""
        self.test_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.samples_dir = self.test_dir / "samples"
        self.simple_project = self.samples_dir / "simple_project.vbp"
        self.complex_project = self.samples_dir / "complex_project.vbp"

    def test_parser_returns_project_object(self):
        """Test that the parser returns a VB6Project object"""
        project = parse_vbp_file(self.simple_project)
        self.assertIsNotNone(project)
        self.assertIsInstance(project, VB6Project)

    def test_simple_project_metadata(self):
        """Test that simple project metadata is correctly parsed"""
        project = parse_vbp_file(self.simple_project)
        self.assertEqual(project.name, "SimpleProject")
        self.assertEqual(project.filename, "simple_project.vbp")
        self.assertEqual(project.path, str(self.samples_dir))

    def test_simple_project_components(self):
        """Test that simple project components are correctly parsed"""
        project = parse_vbp_file(self.simple_project)
        self.assertEqual(len(project.components), 3)

        # Verify forms
        forms = [c for c in project.components if c.component_type == "Form"]
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0].name, "frmMain")

        # Verify modules
        modules = [c for c in project.components if c.component_type == "Module"]
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0].name, "modMain")

        # Verify classes
        classes = [c for c in project.components if c.component_type == "Class"]
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].name, "clsData")

    def test_complex_project_components(self):
        """Test that complex project components are correctly parsed"""
        project = parse_vbp_file(self.complex_project)

        # Verify component counts
        self.assertGreaterEqual(len(project.components), 10)

        forms_count = len([c for c in project.components if c.component_type == "Form"])
        modules_count = len([c for c in project.components if c.component_type == "Module"])
        classes_count = len([c for c in project.components if c.component_type == "Class"])

        self.assertGreaterEqual(forms_count, 5)
        self.assertGreaterEqual(modules_count, 3)
        self.assertGreaterEqual(classes_count, 2)

        # Verify specific components exist
        component_names = [c.name for c in project.components]
        self.assertIn("frmMain", component_names)
        self.assertIn("frmOptions", component_names)
        self.assertIn("modUtility", component_names)
        self.assertIn("clsDatabase", component_names)

    def test_nonexistent_file(self):
        """Test that the parser handles nonexistent files gracefully"""
        nonexistent_file = self.samples_dir / "nonexistent.vbp"
        project = parse_vbp_file(nonexistent_file)
        self.assertIsNone(project)

    def test_component_lookup(self):
        """Test that components can be looked up by name"""
        project = parse_vbp_file(self.simple_project)
        component = project.find_component_by_name("frmMain")
        self.assertIsNotNone(component)
        self.assertEqual(component.component_type, "Form")

        # Case insensitive lookup
        component = project.find_component_by_name("FRMMAIN")
        self.assertIsNotNone(component)
        self.assertEqual(component.name, "frmMain")

        # Nonexistent component
        component = project.find_component_by_name("nonexistent")
        self.assertIsNone(component)


if __name__ == '__main__':
    unittest.main()