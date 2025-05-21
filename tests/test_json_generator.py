import unittest
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.components import VB6Project, VB6Component
from generators.json_generator import export_json


class TestJSONGenerator(unittest.TestCase):
    """Test cases for the JSON export functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_export.json")

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

    def test_export_json(self):
        """Test that JSON file is generated successfully"""
        # Export the JSON
        result = export_json(self.project, self.output_file)

        # Check function result
        self.assertTrue(result)

        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file))

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Verify project metadata
        self.assertIn("project", data)
        self.assertEqual(data["project"]["name"], "TestProject")
        self.assertEqual(data["project"]["path"], self.temp_dir)
        self.assertEqual(data["project"]["filename"], "TestProject.vbp")

        # Verify statistics
        self.assertIn("statistics", data)
        self.assertEqual(data["statistics"]["total_components"], 4)
        self.assertEqual(data["statistics"]["forms"], 2)
        self.assertEqual(data["statistics"]["modules"], 1)
        self.assertEqual(data["statistics"]["classes"], 1)

        # Verify components
        self.assertIn("components", data)
        self.assertEqual(len(data["components"]), 4)

        # Find frmMain component
        frm_main = None
        for comp in data["components"]:
            if comp["name"] == "frmMain":
                frm_main = comp
                break

        self.assertIsNotNone(frm_main)
        self.assertEqual(frm_main["type"], "Form")
        self.assertEqual(frm_main["filename"], "frmMain.frm")
        self.assertEqual(len(frm_main["dependencies"]), 3)
        self.assertIn("frmOptions", frm_main["dependencies"])
        self.assertIn("modUtils", frm_main["dependencies"])
        self.assertIn("clsData", frm_main["dependencies"])

        # Check dependents
        self.assertEqual(len(frm_main["dependents"]), 1)
        self.assertIn("frmOptions", frm_main["dependents"])

    def test_json_unicode_handling(self):
        """Test handling of Unicode characters in the JSON export"""
        # Create a component with Unicode characters
        unicode_component = self.project.add_component("frmÜnicode", "frmUnicode.frm", "Form")
        unicode_component.dependencies = ["çlassÑame"]

        # Export the JSON
        export_json(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find the Unicode component
        unicode_comp = None
        for comp in data["components"]:
            if comp["name"] == "frmÜnicode":
                unicode_comp = comp
                break

        self.assertIsNotNone(unicode_comp)
        self.assertEqual(unicode_comp["name"], "frmÜnicode")
        self.assertIn("çlassÑame", unicode_comp["dependencies"])

    def test_error_handling(self):
        """Test JSON export with simulated failure"""
        # Use a path containing 'CON' and set test_mode=True to force failure
        invalid_path = os.path.join(self.temp_dir, "CON_test.json")

        # Should return False due to test_mode parameter
        result = export_json(self.project, invalid_path, test_mode=True)
        self.assertFalse(result)

    def test_duplicate_dependencies(self):
        """Test handling of duplicate dependencies"""
        # Add duplicate dependencies
        self.form1.dependencies = ["modUtils", "modUtils", "clsData", "clsData"]

        # Export the JSON
        export_json(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find frmMain component
        frm_main = None
        for comp in data["components"]:
            if comp["name"] == "frmMain":
                frm_main = comp
                break

        # Dependencies should be deduplicated
        self.assertEqual(len(frm_main["dependencies"]), 2)
        self.assertIn("modUtils", frm_main["dependencies"])
        self.assertIn("clsData", frm_main["dependencies"])

    def test_json_structure(self):
        """Test the overall structure of the JSON output"""
        # Export the JSON
        export_json(self.project, self.output_file)

        # Read the generated file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check that all required fields are present for each component
        required_fields = ["name", "type", "filename", "dependencies", "dependents",
                           "dependency_count", "dependent_count"]

        for comp in data["components"]:
            for field in required_fields:
                self.assertIn(field, comp)

        # Check that dependency_count matches actual dependencies
        for comp in data["components"]:
            self.assertEqual(comp["dependency_count"], len(comp["dependencies"]))

        # Check that total component count matches actual components
        self.assertEqual(data["statistics"]["total_components"], len(data["components"]))


if __name__ == '__main__':
    unittest.main()