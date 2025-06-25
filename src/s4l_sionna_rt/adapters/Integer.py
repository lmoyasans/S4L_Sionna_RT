import XCore as xc
import logging

logger = logging.getLogger(__name__)

class Integer:
    def __init__(self, initial_value, min=-2147483647, max=2147483647, extra_case = None, name=None): 
        self.value = initial_value
        self.min = min
        self.max = max
        self.extra_case = extra_case
        self.name = name

    def draw(self, parent, name):
        new_prop = xc.PropertyInt(self.value, self.min, self.max)
        if self.name != None:
            new_prop.Description = self.name
        new_prop.OnModified.Connect(self._update)
        parent.Add(name, new_prop)

    def _update(self, property: xc.PropertyInt, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
                return
        self.value = property.Value
        logger.debug(f'[Integer] Update - New value : {self.value}')

    def validate(self):
        if self.value == self.extra_case or (self.value >= self.min and self.value <= self.max):
            return True, ""
        else:
            return False, "Select an integer between {self.min} and {self.max} or the extra case {self.extra_case}"

    def to_format(self, prop_name, results_dir):
        return {prop_name:self.value}
    
