import XCore as xc
import XCoreMath as xcm
import logging

logger = logging.getLogger(__name__)

class Vec2:
    def __init__(self, x,y, label="vector", name=None):
        self.x = x
        self.y = y
        self.label = label
        self.name = name

    def draw(self, parent, name):
        new_prop = xc.PropertyRealTuple((self.x,self.y))
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum): 
        if mod_type != xc.kPropertyModified:
            return

        inner_vec2 = property.Value
        self.x = inner_vec2[0]
        self.y = inner_vec2[1]

    def validate(self):
        return True, ""

    def to_format(self, prop_name, results_dir):
        return {prop_name:(self.x, self.y)}
    
