import logging

import XCore
import XCoreHeadless
from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem

from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties

logger = logging.getLogger(__name__)


class BackgroundScene(TreeItem):
    """
    Defines the usage of any of the base scenes defined in Sionna RT
    """

    def __init__(
        self,
        parent: TreeItem,
    ) -> None:
        """
        
        Creates the properties panel with the selection dropdown
        
        Args:
            parent: The parent tree item (typically the Simulation object)
        """
        super().__init__(parent, icon="icons/XSimulatorUI/SolverSettings.ico")

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Background scene"

        self.config = conf.create_BackgroundScene()
        draw_properties(self,self.config)

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support.
        
        Args:
            state: The serialized state to restore from
        """
        super().__setstate__(state)
        self._properties.Clear()
        draw_properties(self,self.config)

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
        Provides access to the property group configuration options.
        
        These properties will be displayed in the S4L properties panel when the
        solver settings are selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates configuration. 
        
        Returns:
            True if the solver settings are valid, False otherwise
        """
        return True

    def as_api_model(self, results_dir):
        """
        Serializes the antennas in JSON format
        
        Returns:
            Dictionary for JSON serialization
        """
        
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        print("out:")
        print(output)
        print("end")

        return output
