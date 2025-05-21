VERSION 5.00
Begin VB.Form frmMain
   Caption         =   "Simple Project - Main Form"
   ClientHeight    =   4320
   ClientLeft      =   60
   ClientTop       =   345
   ClientWidth     =   6585
   LinkTopic       =   "Form1"
   ScaleHeight     =   4320
   ScaleWidth      =   6585
   StartUpPosition =   2  'CenterScreen
   Begin VB.CommandButton cmdExit
      Caption         =   "E&xit"
      Height          =   495
      Left            =   4800
      TabIndex        =   1
      Top             =   3600
      Width           =   1215
   End
   Begin VB.CommandButton cmdProcess
      Caption         =   "&Process Data"
      Height          =   495
      Left            =   600
      TabIndex        =   0
      Top             =   3600
      Width           =   1215
   End
   Begin VB.Label lblTitle
      Alignment       =   2  'Center
      Caption         =   "Simple VB6 Project"
      BeginProperty Font
         Name            =   "MS Sans Serif"
         Size            =   13.5
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   615
      Left            =   600
      TabIndex        =   2
      Top             =   480
      Width           =   5415
   End
End
Attribute VB_Name = "frmMain"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

' Dependencies:
' - modMain
' - clsData

Private Sub Form_Load()
    ' Call the initialization function from the module
    modMain.InitializeApplication

    ' Set up the form caption
    Me.Caption = "Simple Project v" & App.Major & "." & App.Minor
End Sub

Private Sub cmdProcess_Click()
    ' Create an instance of the data class
    Dim objData As New clsData

    ' Process data
    objData.ProcessData

    MsgBox "Data processing complete!", vbInformation
End Sub

Private Sub cmdExit_Click()
    ' Clean up before exiting
    modMain.CleanupApplication

    ' Exit the application
    Unload Me
End Sub