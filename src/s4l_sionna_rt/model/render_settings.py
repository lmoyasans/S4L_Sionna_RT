import logging

import XCore
import XCoreHeadless
from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties

logger = logging.getLogger(__name__)


class RenderSettings(TreeItem):
    """
    Manages general render and visualization parameters and preferences.
    
    These settings affect the overall visualization of the rendered
    image but are not directly related to the physics being modeled.
    """

    def __init__(
        self,
        parent: TreeItem,
    ) -> None:
        """
        Initializes settings with default values.
        
        Creates the properties panel with basic configuration 
        
        Args:
            parent: The parent tree item (typically the Simulation object)
        """
        super().__init__(parent, icon="icons/XSimulatorUI/SetupSettings.ico")

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Render Settings"
        self.config = conf.create_RenderSettings()
        draw_properties(self,self.config)

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support .
        
        Args:
            state: The serialized state to restore from
        """
        super().__setstate__(state)

    @property
    def description(self) -> str:
        """Gets the descriptive name as shown in the UI."""
        return self._properties.Description

    @description.setter
    def description(self, value: str) -> None:
        """Sets the descriptive name as shown in the UI."""
        self._properties.Description = value

    @property
    def properties(self) -> XCore.PropertyGroup:
        """
        Provides access to the property group containing general setup options.
        
        These properties will be displayed in the S4L properties panel when the
        setup settings are selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates that the settings are properly configured.
        
        Returns:
            True if the settings are valid, False otherwise
        """
        for i in self.config.__dict__.keys():
            result, message = self.config.__dict__[i].validate()
            if not result:
                self.status_icons = [
                "icons/TaskManager/Warning.ico",
                ]
                self.status_icons_tooltip = message
                return False
        return True

    def as_api_model(self, results_dir):
        """
        Serialization in the appropriate format
        
        Returns:
            A dictionary with the render parameters
        """

        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))

        return {"Render_Settings": output}
