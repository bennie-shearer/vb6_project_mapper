"""
Form Relationships Diagram Generation Module
Focuses on visualizing form-to-form relationships
"""

def generate_form_relationships_diagram(f, project):
    """Generate diagram showing only form-to-form relationships"""
    import html

    f.write("graph LR\n")

    # Get all Form components
    forms = [comp for comp in project.components if comp.component_type == "Form"]

    # Add node definitions
    node_ids = {}  # Map component names to node IDs
    for i, form in enumerate(forms):
        node_id = f"form{i}"
        node_ids[form.name] = node_id

        # Escape form name for Mermaid
        safe_name = html.escape(form.name).replace('\\', '\\\\').replace('"', '\\"')
        f.write(f'    {node_id}["{safe_name}"]\n')

    # Add form-to-form connections
    edges_added = set()
    for form in forms:
        if form.name in node_ids:
            source_id = node_ids[form.name]

            # Add dependencies to other forms
            for dep in set(form.dependencies):
                dep_comp = project.find_component_by_name(dep)
                if dep_comp and dep_comp.component_type == "Form" and dep_comp.name in node_ids:
                    target_id = node_ids[dep_comp.name]
                    edge_key = f"{source_id}->{target_id}"

                    if edge_key not in edges_added:
                        f.write(f"    {source_id} --> {target_id}\n")
                        edges_added.add(edge_key)

    # Add CSS for forms
    f.write("""
    classDef default fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1
    """)