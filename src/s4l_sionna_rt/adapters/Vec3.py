import XCore as xc
import XCoreMath as xcm
import logging

logger = logging.getLogger(__name__)

class Vec3:
    def __init__(self, x,y,z, label="vector", name=None):
        self.x = x
        self.y = y
        self.z = z
        self.label = label
        self.name = name

    def draw(self, parent, name):
        new_prop = xcm.PropertyVec3(xcm.Vec3(self.x,self.y,self.z))
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum): 
        if mod_type != xc.kPropertyModified:
            return

        inner_vec3 = property.Value
        self.x = inner_vec3[0]
        self.y = inner_vec3[1]
        self.z = inner_vec3[2]

    def validate(self):
        return True, ""

    def to_format(self, prop_name, results_dir):
        return  {prop_name:[self.x, self.y, self.z]}
    
