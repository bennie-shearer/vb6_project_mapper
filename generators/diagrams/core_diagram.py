"""
Core Architecture Diagram Generation Module
Creates a diagram showing the most connected components
"""

def generate_core_architecture_diagram(f, project):
    """Generate diagram showing the core architecture components"""
    import html
    from utils.helpers import get_dependents

    f.write("graph LR\n")

    # Find the 20 most connected components
    MAX_COMPONENTS = 20
    component_connections = []

    for comp in project.components:
        dependents_count = len(get_dependents(project, comp))
        dependencies_count = len(set(comp.dependencies))
        total_connections = dependents_count + dependencies_count
        component_connections.append((comp, total_connections))

    # Sort by total connections
    component_connections.sort(key=lambda x: x[1], reverse=True)
    components_to_render = [comp for comp, _ in component_connections[:MAX_COMPONENTS]]

    # Add node definitions with simplified IDs
    node_ids = {}  # Map component names to node IDs
    for i, component in enumerate(components_to_render):
        node_id = f"core{i}"
        node_ids[component.name] = node_id

        # Escape component name for Mermaid
        safe_name = html.escape(component.name).replace('\\', '\\\\').replace('"', '\\"')

        # Add CSS class based on component type
        node_class = "cls" if component.component_type.lower() == "class" else component.component_type.lower()
        f.write(f'    {node_id}["{safe_name}"]:::{node_class}\n')

    # Add connections
    edges_added = set()
    for component in components_to_render:
        if component.name in node_ids:
            source_id = node_ids[component.name]

            # Add dependencies
            for dep in set(component.dependencies):
                dep_comp = project.find_component_by_name(dep)
                if dep_comp and dep_comp.name in node_ids:
                    target_id = node_ids[dep_comp.name]
                    edge_key = f"{source_id}->{target_id}"

                    if edge_key not in edges_added:
                        f.write(f"    {source_id} --> {target_id}\n")
                        edges_added.add(edge_key)

    # Add CSS classes for styling
    f.write("""
    classDef form fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1
    classDef module fill:#e8f5e9,stroke:#4caf50,stroke-width:2px,color:#1b5e20
    classDef cls fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100
    classDef usercontrol fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#4a148c
    classDef propertypage fill:#fffde7,stroke:#ffc107,stroke-width:2px,color:#ff6f00
    classDef designer fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#b71c1c
    """)