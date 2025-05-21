def count_components_by_type(project, component_type):
    """Count components by type"""
    return sum(1 for component in project.components if component.component_type == component_type)


def has_dependents(project, component):
    """Check if a component has any dependents"""
    return any(component.name in other.dependencies for other in project.components if other != component)


def get_dependents(project, component):
    """Get all components that depend on this component"""
    return [other for other in project.components if component.name in other.dependencies]