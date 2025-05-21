class VB6Component:
    """Represents a component in a VB6 project"""

    def __init__(self, name, filename, component_type):
        self.name = name
        self.filename = filename
        self.component_type = component_type
        self.dependencies = []
        self.content = ""


class VB6Project:
    """Represents a VB6 project and all its components"""

    def __init__(self):
        self.name = ""
        self.path = ""
        self.filename = ""
        self.components = []

    def add_component(self, name, filename, component_type):
        """Add a component to the project"""
        component = VB6Component(name, filename, component_type)
        self.components.append(component)
        return component

    def find_component_by_name(self, name):
        """Find a component by its name"""
        for component in self.components:
            if component.name.lower() == name.lower():
                return component
        return None