import XCore as xc
import XCoreMath as xcm
import logging

logger = logging.getLogger(__name__)

class Boolean:
    def __init__(self, val = False, name=None): 
        self.value = val
        self.name = name

    def draw(self, parent, name):
        new_prop = xc.PropertyBool(self.value)
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
            return
        
        self.value = property.Value

    def validate(self):
        return True, ""

    def to_format(self, prop_name, results_dir):
        return {prop_name:self.value}
    