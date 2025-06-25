import XCore as xc
import logging

logger = logging.getLogger(__name__)

class Base:
    def __init__(self):
        pass

    def draw(self, parent, name):
        pass

    def _update(self, property: xc.PropertyReal, mod_type: xc.PropertyModificationTypeEnum):
        pass

    def validate(self):
        return True, ""


    def to_format(self, prop_name:str, results_dir:str):
        return prop_name
    
