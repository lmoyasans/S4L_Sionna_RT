import XCore as xc
import XCoreMath as xcm
import XCoreHeadless
from s4l_sionna_rt.solver.driver import api_models as conf
from s4l_sionna_rt.model.draw import draw_properties
import logging

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, name = None):
        logger.debug(id(self))
        self._properties: XCoreHeadless.DialogOptions = XCoreHeadless.DialogOptions()
        if name != None:
            self._properties.Description = name

    def draw(self, parent, name):
        self._properties.Clear()

        self.config = conf.create_Camera()

        draw_properties(self, self.config)
        parent.Add(name, self._properties)

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
            return

    def validate(self):
        for i in self.config.__dict__.keys():
            result, message = self.config.__dict__[i].validate()
            if not result:
                return False, "Camera: " + message
        return True, ""

    def to_format(self, prop_name, results_dir): 
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        return {prop_name:output}
    
