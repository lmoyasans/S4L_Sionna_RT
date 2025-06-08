import XCore as xc
import logging

logger = logging.getLogger(__name__)

class Real:
    def __init__(self, initial_value, min=-1.7976931348623157e+308, max=1.7976931348623157e+308, extra_case=None, name=None):
        self.value = initial_value
        self.min = min
        self.max = max
        self.extra_case = extra_case
        self.name = name

    def draw(self, parent, name):
        new_prop = xc.PropertyReal(self.value)
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def _update(self, property: xc.PropertyReal, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
                return
        self.value = property.Value
        logger.debug(f'[Real] Update - New value : {self.value}')

    def validate(self):
        if self.value == self.extra_case or (self.value >= self.min and self.value <= self.max):
            return True, ""
        else:
            return False, f"Select a real value between {self.min} and {self.max} or the extra case {self.extra_case}"


    def to_format(self, prop_name:str, results_dir:str):
        if self.value == self.extra_case:
            return  {prop_name:None}
        return {prop_name:self.value}
    
