Attribute VB_Name = "modMain"
Option Explicit

' Dependencies:
' - clsData

' Global variables
Public g_bApplicationInitialized As Boolean
Public g_sAppPath As String

' Initialize the application
Public Sub InitializeApplication()
    ' Set the application path
    g_sAppPath = App.Path

    ' Set initialization flag
    g_bApplicationInitialized = True

    ' Log initialization
    Debug.Print "Application initialized at " & Now()
End Sub

' Clean up the application
Public Sub CleanupApplication()
    ' Create a data object for cleanup
    Dim objData As clsData
    Set objData = New clsData

    ' Clean up data
    objData.CleanupData

    ' Release the object
    Set objData = Nothing

    ' Set initialization flag
    g_bApplicationInitialized = False

    ' Log cleanup
    Debug.Print "Application shut down at " & Now()
End Sub

' Helper function to check if a file exists
Public Function FileExists(ByVal sFilePath As String) As Boolean
    On Error Resume Next
    FileExists = (Dir(sFilePath) <> "")
    On Error GoTo 0
End Function

' Format a date value as a string
Public Function FormatDateString(ByVal dDate As Date) As String
    FormatDateString = Format(dDate, "yyyy-mm-dd")
End Function