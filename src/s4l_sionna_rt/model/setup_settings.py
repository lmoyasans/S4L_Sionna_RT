import logging

import XCore
import XCoreHeadless
from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties

logger = logging.getLogger(__name__)


class SetupSettings(TreeItem):
    """
    Manages general simulation setup parameters and preferences.
    
    This class provides control over basic simulation settings.
    """

    def __init__(
        self,
        parent: TreeItem,
    ) -> None:
        """
        Initializes setup settings with default values.
        
        Creates the properties panel with basic simulation configuration options
        such as logging level for the solver.
        
        Args:
            parent: The parent tree item (typically the Simulation object)
        """
        super().__init__(parent, icon="icons/XSimulatorUI/SetupSettings.ico")

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Setup Settings"
        self.config = conf.create_SetupSettings()
        draw_properties(self,self.config)

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support for loading saved setup settings.
        
        Args:
            state: The serialized state to restore from
        """
        super().__setstate__(state)

    @property
    def description(self) -> str:
        """Gets the descriptive name of the setup settings as shown in the UI."""
        return self._properties.Description

    @description.setter
    def description(self, value: str) -> None:
        """Sets the descriptive name of the setup settings as shown in the UI."""
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
        Validates that the setup settings are properly configured.
        
        Checks that all required settings have valid values for simulation execution.
        
        Returns:
            True if the setup settings are valid, False otherwise
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
        Converts the setup settings to a the appropriate format.
        
        Returns:
            A dictionary object with the setup parameters
        """
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, str(results_dir)))

        return {"Setup_settings":output}
