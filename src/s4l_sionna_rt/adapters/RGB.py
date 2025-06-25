import XCore as xc
import XCoreMath as xcm
import logging

logger = logging.getLogger(__name__)

class RGB:
    def __init__(self, r=0,g=0,b=0, name=None): 
        self.r = r
        self.g = g
        self.b = b
        self.name=name

    def draw(self, parent, name):
        new_prop = xcm.PropertyVec3(xcm.Vec3(self.r,self.g,self.b))
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def validate(self):
        if (self.r < 0.0 or self.r > 1.0) or (self.g < 0.0 or self.g > 1.0) or (self.b < 0.0 or self.b > 1.0):
            return False, "Color values must be between 0 and 1"
        return True, ""

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
            return
        
        inner_vec3 = property.Value
        self.r = inner_vec3[0]
        self.g = inner_vec3[1]
        self.b = inner_vec3[2]
        
        if self.validate():
            logger.debug(f"Values color: {self.r} {self.g} {self.b}")

    def to_format(self, prop_name, results_dir):
        return {prop_name:(self.r,self.g,self.b)}
    