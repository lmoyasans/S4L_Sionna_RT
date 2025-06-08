import logging

import XCore
import XCoreHeadless
from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem
from s4l_sionna_rt.solver.driver import api_models as conf
import s4l_sionna_rt.model.transmitters as transmitters
import s4l_sionna_rt.model.receivers as receivers
from .draw import draw_properties

logger = logging.getLogger(__name__)


class Antennas(TreeItem):
    """
    General class for both transmitters and receivers. 
    Includes the parameters for the antenna arrays.
    """

    def __init__(
        self,
        parent: TreeItem,
    ) -> None:
        """
        Initializes antenna arrayswith default parameters as well as transmitter
        and receiver children 
        
        Args:
            parent: The parent tree item (typically the Simulation object)
        """
        super().__init__(parent, icon="icons/XSimulatorUI/SolverSettings.ico")

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Antennas"
        
        self._transmitters = transmitters.Transmitters(self)
        self._receivers = receivers.Receivers(self)

        self.config = conf.create_Antenna()
        draw_properties(self,self.config)
        self.is_expanded = True

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support .
        
        Args:
            state: The serialized state to restore from
        """
        super().__setstate__(state)

    @property
    def description(self) -> str:
        """Gets the descriptive name  as shown in the UI."""
        return self._properties.Description

    @description.setter
    def description(self, value: str) -> None:
        """Sets the descriptive name as shown in the UI."""
        self._properties.Description = value

    @property
    def properties(self) -> XCore.PropertyGroup:
        """
        Provides access to the property group containing configuration options.
        
        These properties will be displayed in the S4L properties panel when the
        solver settings are selected in the UI.
        """
        return self._properties

    @property
    def transmitters(self) -> transmitters.Transmitters:
        return self._transmitters

    @property
    def receivers(self) -> receivers.Receivers:
        return self._receivers

    def validate(self) -> bool:
        """
        Validates that the arrays are properly configured.
        
        Blocks execution unless transmitters have been set up.
        
        Returns:
            True if the solver settings are valid, False otherwise
        """
        if len(self._transmitters.elements) == 0:
            self._transmitters.status_icons = [
                "icons/TaskManager/Warning.ico",
            ]
            self._transmitters.status_icons_tooltip = "No transmitters defined"
            return False

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
        Serializes the antennas in JSON format
        
        Returns:
            Dictionary for JSON serialization
        """
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        

        transm = {}
        for num, tr in enumerate(self._transmitters.elements):
            transm.update(tr.as_api_model("tr_" + str(num), results_dir))
        
        output.update({"transmitters":transm})

        recev = {}
        for num, rv in enumerate(self._receivers.elements):
            recev.update(rv.as_api_model("rv_" + str(num), results_dir))
        
        output.update({"receivers":recev})

        return {"Antennas":output}
