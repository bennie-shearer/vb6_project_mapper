import unittest
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.vbp_parser import parse_vbp_file
from analyzers.dependency_analyzer import analyze_dependencies
from models.components import VB6Project, VB6Component


class TestDependencyAnalyzer(unittest.TestCase):
    """Test cases for the dependency analyzer"""

    def setUp(self):
        """Set up test projects and environment"""
        self.test_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.samples_dir = self.test_dir / "samples"

        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create a simple test project manually
        self.test_project = VB6Project()
        self.test_project.name = "TestProject"
        self.test_project.path = self.temp_dir

        # Create test components
        self.form1 = self.test_project.add_component("frmMain", "frmMain.frm", "Form")
        self.form2 = self.test_project.add_component("frmOptions", "frmOptions.frm", "Form")
        self.module1 = self.test_project.add_component("modUtils", "modUtils.bas", "Module")
        self.class1 = self.test_project.add_component("clsData", "clsData.cls", "Class")

        # Create test files with dependencies
        self._create_test_file("frmMain.frm", """
        VERSION 5.00
        Begin VB.Form frmMain
           Caption         =   "Main Form"
           ClientHeight    =   3090
           ClientLeft      =   60
           ClientTop       =   450
           ClientWidth     =   4680
           LinkTopic       =   "Form1"
           ScaleHeight     =   3090
           ScaleWidth      =   4680
           StartUpPosition =   3  'Windows Default
           Begin VB.CommandButton cmdOptions
              Caption         =   "Options"
              Height          =   495
              Left            =   1680
              TabIndex        =   0
              Top             =   1320
              Width           =   1215
           End
        End
        Attribute VB_Name = "frmMain"
        Attribute VB_GlobalNameSpace = False
        Attribute VB_Creatable = False
        Attribute VB_PredeclaredId = True
        Attribute VB_Exposed = False
        Option Explicit

        Private Sub cmdOptions_Click()
            ' Direct reference to form
            frmOptions.Show

            ' Reference to module
            Call modUtils.LogMessage("Options opened")

            ' Create object instance
            Dim data As New clsData
            data.LoadData
        End Sub
        """)

        self._create_test_file("frmOptions.frm", """
        VERSION 5.00
        Begin VB.Form frmOptions
           Caption         =   "Options"
           ClientHeight    =   3090
           ClientLeft      =   60
           ClientTop       =   450
           ClientWidth     =   4680
           LinkTopic       =   "Form1"
           ScaleHeight     =   3090
           ScaleWidth      =   4680
           StartUpPosition =   3  'Windows Default
        End
        Attribute VB_Name = "frmOptions"
        Attribute VB_GlobalNameSpace = False
        Attribute VB_Creatable = False
        Attribute VB_PredeclaredId = True
        Attribute VB_Exposed = False
        Option Explicit

        Private Sub Form_Load()
            ' Reference to module
            modUtils.InitializeForm Me

            ' Reference back to main form - creates circular dependency
            frmMain.Caption = "Main - Options Open"
        End Sub
        """)

        self._create_test_file("modUtils.bas", """
        Attribute VB_Name = "modUtils"
        Option Explicit

        Public Sub LogMessage(message As String)
            Debug.Print message
        End Sub

        Public Sub InitializeForm(frm As Form)
            frm.Caption = frm.Caption & " - Initialized"

            ' Use class
            Dim data As clsData
            Set data = New clsData
            data.LoadData
        End Sub
        """)

        self._create_test_file("clsData.cls", """
        VERSION 1.0 CLASS
        BEGIN
          MultiUse = -1  'True
          Persistable = 0  'NotPersistable
          DataBindingBehavior = 0  'vbNone
          DataSourceBehavior  = 0  'vbNone
          MTSTransactionMode  = 0  'NotAnMTSObject
        END
        Attribute VB_Name = "clsData"
        Attribute VB_GlobalNameSpace = False
        Attribute VB_Creatable = True
        Attribute VB_PredeclaredId = False
        Attribute VB_Exposed = False
        Option Explicit

        Public Sub LoadData()
            ' No dependencies to other components
        End Sub
        """)

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def _create_test_file(self, filename, content):
        """Helper to create test files"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='latin-1') as f:
            f.write(content)

    def test_analyze_dependencies(self):
        """Test that dependencies are correctly identified"""
        # Run the dependency analyzer
        analyze_dependencies(self.test_project)

        # Check frmMain dependencies
        self.assertIn("frmOptions", self.form1.dependencies)
        self.assertIn("modUtils", self.form1.dependencies)
        self.assertIn("clsData", self.form1.dependencies)

        # Check frmOptions dependencies
        self.assertIn("modUtils", self.form2.dependencies)
        self.assertIn("frmMain", self.form2.dependencies)

        # Check modUtils dependencies
        self.assertIn("clsData", self.module1.dependencies)

        # Check clsData dependencies (should be empty)
        self.assertEqual(len(self.class1.dependencies), 0)

    def test_circular_dependencies(self):
        """Test that circular dependencies are detected"""
        # Run the dependency analyzer
        analyze_dependencies(self.test_project)

        # Verify circular dependency between frmMain and frmOptions
        self.assertIn("frmOptions", self.form1.dependencies)
        self.assertIn("frmMain", self.form2.dependencies)

    def test_dependency_patterns(self):
        """Test different dependency patterns are detected"""
        # Create a test component with various reference patterns
        test_component = self.test_project.add_component("frmTest", "frmTest.frm", "Form")

        # Create file with different dependency patterns
        self._create_test_file("frmTest.frm", """
        VERSION 5.00
        Begin VB.Form frmTest
           Caption         =   "Test Form"
           ClientHeight    =   3090
           ClientLeft      =   60
           ClientTop       =   450
           ClientWidth     =   4680
           LinkTopic       =   "Form1"
           ScaleHeight     =   3090
           ScaleWidth      =   4680
           StartUpPosition =   3  'Windows Default
        End
        Attribute VB_Name = "frmTest"
        Attribute VB_GlobalNameSpace = False
        Attribute VB_Creatable = False
        Attribute VB_PredeclaredId = True
        Attribute VB_Exposed = False
        Option Explicit

        ' Direct reference
        Private Sub Form_Load()
            frmMain.Show
        End Sub

        ' Reference with dot notation
        Private Sub Command1_Click()
            modUtils.LogMessage "Test"
        End Sub

        ' Object creation
        Private Sub Command2_Click()
            Dim data As New clsData
        End Sub

        ' Variable declaration
        Private Sub Command3_Click()
            Dim f As frmOptions
            Set f = New frmOptions
        End Sub
        """)

        # Run the dependency analyzer
        analyze_dependencies(self.test_project)

        # Check that all patterns are detected
        self.assertIn("frmMain", test_component.dependencies)
        self.assertIn("modUtils", test_component.dependencies)
        self.assertIn("clsData", test_component.dependencies)
        self.assertIn("frmOptions", test_component.dependencies)

    def test_missing_files(self):
        """Test handling of missing files"""
        # Add a component with a missing file
        missing_component = self.test_project.add_component("modMissing", "modMissing.bas", "Module")

        # Run the dependency analyzer - should not crash
        analyze_dependencies(self.test_project)

        # The component should have empty content and no dependencies
        self.assertEqual(missing_component.content, "")
        self.assertEqual(len(missing_component.dependencies), 0)

    def test_real_project_parsing(self):
        """Test with a real sample project if available"""
        simple_project_path = self.samples_dir / "simple_project.vbp"

        if simple_project_path.exists():
            project = parse_vbp_file(simple_project_path)
            self.assertIsNotNone(project)

            # Run the dependency analyzer - should not crash
            analyze_dependencies(project)

            # Should find at least some dependencies
            total_dependencies = sum(len(c.dependencies) for c in project.components)
            self.assertGreater(total_dependencies, 0)


if __name__ == '__main__':
    unittest.main()