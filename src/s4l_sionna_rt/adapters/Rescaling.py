import XCore as xc
import XCoreMath as xcm
import XCoreHeadless
from s4l_sionna_rt.solver.driver import api_models as conf
from s4l_sionna_rt.model.draw import draw_properties
import logging

logger = logging.getLogger(__name__)

class Rescaling:
    def __init__(self, name=None):
        self._properties: XCoreHeadless.DialogOptions = XCoreHeadless.DialogOptions()
        if name != None:
            self._properties.Description = name
        self.config = conf.create_Rescaling()

    def draw(self, parent, name):
        self._properties.Clear()

        draw_properties(self, self.config)
        parent.Add(name, self._properties)
        for prop in self._properties:
            prop.Visible = False
        self._properties.activate.Visible =True
        self._properties.activate.OnModified.Connect(self._update)

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
            return
        if self._properties.activate.Value == False:
            for prop in self._properties:
                prop.Visible = False
            self._properties.activate.Visible =True
        else:
            for prop in self._properties:
                prop.Visible = True

    def validate(self):
        for i in self.config.__dict__.keys():
            result, message = self.config.__dict__[i].validate()
            if not result:
                return False, "Rescaling:"+ message
            if self._properties.activate.Value == True:
                if self._properties.rm_vmax.Value < self._properties.rm_vmin.Value:
                    return False, "Rescaling: VMin cannot be higher than VMax"
        return True, ""

    def to_format(self, prop_name, results_dir): 
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        return {prop_name:output}
    
