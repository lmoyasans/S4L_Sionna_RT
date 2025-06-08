import XCore as xc
import XCoreMath as xcm
import logging
import XCoreHeadless
from s4l_sionna_rt.model.draw import draw_properties
from typing import Optional

logger = logging.getLogger(__name__)

class Toggle:
    def __init__(self, classes, names, prop_names: Optional[list[str]] = None, name=None): 
        self.value = 0
        self.classes = classes
        self.options = names
        self._properties: XCoreHeadless.DialogOptions = XCoreHeadless.DialogOptions()
        self.prop_names = prop_names
        self.parent = None
        self.name = name
        if self.name != None:
            self._properties.Description = self.name

    
    def draw(self, parent, name, redraw=False):
        self.parent = parent
        self.name = name
        self._properties.Clear()
        new_prop = xc.PropertyEnum(
                self.options,self.value
        )
        self._properties.Add("Change type of input", new_prop)
        new_prop.OnModified.Connect(self._update)
        if self.prop_names!=None:
            self.classes[self.value].draw(self._properties, self.prop_names[self.value])
        else:
            self.classes[self.value].draw(self._properties, "")
        if not redraw:
            parent.Add(name, self._properties)
    
    def validate(self):
        return self.classes[self.value].validate()

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
            return
        self.value = property.Value
        self.draw(self.parent, self.name, redraw=True)

    def to_format(self, prop_name, results_dir):
        return {prop_name:self.classes[self.value].to_format(self.options[self.value], results_dir)}
    