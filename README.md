# VB6 Project Mapper

A Python utility for analyzing and visualizing Visual Basic 6.0 project structure and dependencies.

![VB6 Project Mapper Logo](img/vb6_project_mapper_logo.png)

## Overview

VB6 Project Mapper is a tool designed to help developers working with legacy Visual Basic 6.0 applications. It analyzes `.vbp` project files and generates interactive visualizations of component relationships, making it easier to understand complex codebases.

## Features

- 📊 **Comprehensive Analysis**: Analyzes forms, modules, classes, and other VB6 components
- 🔄 **Dependency Mapping**: Identifies and visualizes relationships between components
- 📈 **Multiple Visualization Views**:
  - Core Architecture View: Shows the most connected components
  - Form Relationships View: Focuses on form-to-form interactions
  - Business Logic View: Highlights class dependencies
  - Focus Mode: Interactive explorer for specific components
- 🔍 **Interactive Reports**: Search, filter, and explore component relationships
- 💾 **Export Options**: Save as HTML, JSON, SVG, or PNG
- 🛠️ **Command-line Interface**: Easily integrate into build processes or workflows
- 📝 **Detailed Logging**: Comprehensive logging with different severity levels

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vb6-project-mapper.git
   cd vb6-project-mapper
   ```

2. No additional dependencies are required beyond Python's standard library.

## Usage

### Basic Usage

```
python main.py path/to/your/project.vbp
```

This will generate an HTML report at `path/to/your/project_CodeMap.html`.

### Advanced Options

```
python main.py path/to/your/project.vbp -o custom_output.html -j -v
```

Options:
- `-o, --output`: Specify a custom output filename
- `-j, --json`: Also export the analysis as JSON
- `-v, --verbose`: Enable detailed debug logging
- `-q, --quiet`: Suppress console output except errors

## Generated Report

The HTML report includes:

- Project summary with component counts
- Interactive component browser
- Searchable dependency table
- Multiple interactive diagrams with zoom and pan
- Export options for diagrams

## Integration with Other Tools

VB6 Project Mapper works well with several complementary tools:

### Source Control
- **Git/SVN**: Run the mapper on different versions to track dependency evolution
- Use repository hooks to automatically analyze projects when code changes

### Continuous Integration
- **Jenkins/Azure DevOps**: Integrate into CI/CD pipelines to monitor dependency changes
- Set up alerts for new circular dependencies

### Documentation
- **Confluence/SharePoint**: Publish reports for team access
- Create custom dashboards with dependency metrics

### Migration Planning
- Use dependency data to plan VB6 to .NET migration strategies
- Identify isolated components for easier migration

## Logging System

VB6 Project Mapper includes a comprehensive logging system:

- Log files are organized by severity level (debug, info, warning, error, critical)
- Each run gets a unique identifier for easy tracking
- Configuration file (`logging_config.json`) controls log behavior
- Command-line options can override logging levels

## Project Structure

```
VB6-Project-Mapper/
│
├── main.py                     # Main entry point and CLI
│
├── parsers/
│   ├── __init__.py
│   └── vbp_parser.py           # VB6 project file parser
│
├── models/
│   ├── __init__.py
│   └── components.py           # Data models for VB6 components
│
├── analyzers/
│   ├── __init__.py
│   └── dependency_analyzer.py  # Component dependency analyzer
│
├── generators/
│   ├── __init__.py
│   ├── html_generator.py       # HTML report generator
│   ├── json_generator.py       # JSON export functionality
│   │
│   └── diagrams/
│       ├── __init__.py
│       ├── core_diagram.py     # Main architecture diagram generator
│       ├── form_diagram.py     # Form relationships diagram generator
│       ├── class_diagram.py    # Business logic diagram generator
│       └── mermaid_script.py   # Mermaid.js integration utilities
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py              # Utility functions
│   └── logger.py               # Logging system
│
└── logs/                       # Log directories
    ├── debug/
    ├── info/
    ├── warning/
    ├── error/
    └── critical/
```

## Example Output

When you run the tool on a VB6 project, you'll get an interactive HTML report that looks like this:

```
[Your Project Name] - Code Map

Project Summary
---------------
Forms: XX
Modules: XX
Classes: XX
...
Total: XX

[Interactive component browser]
[Dependency visualizations]
[Export options]
```

## Future Enhancements

- Additional visualization types
- Enhanced filtering options
- Support for other VB project types
- Component code quality analysis
- Automatic migration recommendations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Mermaid.js Project](https://mermaid.js.org/) for diagram rendering
- [PyCharm by JetBrains s.r.o.](https://www.jetbrains.com/pycharm/)
- [Claude by Anthropic PBC](https://www.anthropic.com/)

## Author

Bennie Shearer (Retired)

---

*This tool was inspired by the need to assist developers working with legacy VB6 applications.*
