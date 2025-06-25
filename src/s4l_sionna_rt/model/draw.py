import XCore as xc
from dataclasses import fields

def draw_properties(cls, config):
    """
    Function util for automatic drawing of the properties 
    using dataclasses and adapters defined in the API model files
    
    """
    for field in fields(config):
        name = field.name
        # type_field = field.type
        prop = getattr(config, name)

        # Draw onto the GUI
        prop.draw(cls._properties, name)