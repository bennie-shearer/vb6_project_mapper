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

' Private variables
Private m_sDataSource As String
Private m_bDataLoaded As Boolean

' Initialize the class
Private Sub Class_Initialize()
    ' Set default values
    m_sDataSource = "default.dat"
    m_bDataLoaded = False
End Sub

' Clean up the class
Private Sub Class_Terminate()
    ' Ensure data is cleaned up
    If m_bDataLoaded Then
        CleanupData
    End If
End Sub

' Process the data
Public Sub ProcessData()
    ' Check if data is loaded
    If Not m_bDataLoaded Then
        LoadData
    End If

    ' Simulate data processing
    Debug.Print "Processing data from " & m_sDataSource

    ' Perform some calculations
    Dim i As Integer
    For i = 1 To 5
        Debug.Print "Processing item " & i
        ' Simulate processing delay
        Sleep 100
    Next i

    Debug.Print "Data processing complete"
End Sub

' Load the data
Public Sub LoadData()
    ' Check if the data source exists
    If modMain.FileExists(modMain.g_sAppPath & "\" & m_sDataSource) Then
        Debug.Print "Loading data from " & m_sDataSource
    Else
        Debug.Print "Data source not found, using default values"
    End If

    ' Set the loaded flag
    m_bDataLoaded = True
End Sub

' Clean up the data
Public Sub CleanupData()
    ' Simulate cleanup
    Debug.Print "Cleaning up data"

    ' Reset the loaded flag
    m_bDataLoaded = False
End Sub

' Set the data source
Public Property Let DataSource(ByVal sSource As String)
    m_sDataSource = sSource
    ' Reset the loaded flag when the source changes
    m_bDataLoaded = False
End Property

' Get the data source
Public Property Get DataSource() As String
    DataSource = m_sDataSource
End Property