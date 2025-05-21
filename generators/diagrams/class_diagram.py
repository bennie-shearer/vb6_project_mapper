"""
Business Logic Diagram Generation Module
Focuses on visualizing class components and their relationships
"""


def generate_business_logic_diagram(f, project):
    """Generate diagram showing classes and their dependencies"""
    import html

    f.write("graph LR\n")

    # Get all Class components
    classes = [comp for comp in project.components if comp.component_type == "Class"]

    # Add class nodes
    node_ids = {}  # Map component names to node IDs
    for i, cls in enumerate(classes):
        node_id = f"class{i}"
        node_ids[cls.name] = node_id

        # Escape class name for Mermaid
        safe_name = html.escape(cls.name).replace('\\', '\\\\').replace('"', '\\"')
        f.write(f'    {node_id}["{safe_name}"]\n')

    # Add related component nodes (those that classes depend on or that depend on classes)
    related_components = set()
    for cls in classes:
        # Add components that this class depends on
        for dep in set(cls.dependencies):
            dep_comp = project.find_component_by_name(dep)
            if dep_comp and dep_comp.component_type != "Class":
                related_components.add(dep_comp)

        # Add components that depend on this class
        for comp in project.components:
            if comp.component_type != "Class" and cls.name in comp.dependencies:
                related_components.add(comp)

    # Add related component nodes
    for i, comp in enumerate(related_components):
        if comp.name not in node_ids:  # Avoid duplicates
            node_id = f"related{i}"
            node_ids[comp.name] = node_id

            # Escape component name for Mermaid
            safe_name = html.escape(comp.name).replace('\\', '\\\\').replace('"', '\\"')

            # Add CSS class based on component type
            # FIXED: Use "cls" for Class components instead of "class"
            node_class = "cls" if comp.component_type == "Class" else comp.component_type.lower()
            f.write(f'    {node_id}["{safe_name}"]:::{node_class}\n')

    # Add connections
    edges_added = set()

    # Class dependencies
    for cls in classes:
        if cls.name in node_ids:
            source_id = node_ids[cls.name]

            for dep in set(cls.dependencies):
                dep_comp = project.find_component_by_name(dep)
                if dep_comp and dep_comp.name in node_ids:
                    target_id = node_ids[dep_comp.name]
                    edge_key = f"{source_id}->{target_id}"

                    if edge_key not in edges_added:
                        f.write(f"    {source_id} --> {target_id}\n")
                        edges_added.add(edge_key)

    # Components that depend on classes
    for comp in related_components:
        if comp.name in node_ids:
            source_id = node_ids[comp.name]

            for dep in set(comp.dependencies):
                dep_comp = project.find_component_by_name(dep)
                if dep_comp and dep_comp.component_type == "Class" and dep_comp.name in node_ids:
                    target_id = node_ids[dep_comp.name]
                    edge_key = f"{source_id}->{target_id}"

                    if edge_key not in edges_added:
                        f.write(f"    {source_id} --> {target_id}\n")
                        edges_added.add(edge_key)

    # Add styling classes - FIXED: changed "class" to "cls" to avoid Mermaid keyword conflict
    f.write("""
    classDef cls fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef form fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1
    classDef module fill:#e8f5e9,stroke:#4caf50,stroke-width:2px,color:#1b5e20
    classDef usercontrol fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#4a148c
    classDef propertypage fill:#fffde7,stroke:#ffc107,stroke-width:2px,color:#ff6f00
    classDef designer fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#b71c1c
    """)
