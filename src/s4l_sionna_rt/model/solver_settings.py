import logging

import XCore
import XCoreHeadless
from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties
import asyncio

logger = logging.getLogger(__name__)


class SolverSettings(TreeItem):
    """
    Manages numerical solver parameters that control the solution process.
    
    This class provides configuration options for the numerical algorithms used to
    execute the Radio Map and Path modes. These settings directly impact the accuracy, 
    stability, and performance of the simulation.
    """

    def __init__(
        self,
        parent: TreeItem,
    ) -> None:
        """
        Initializes solver settings with default algorithm parameters.
        
        Creates the properties panel with options for configuring the solver, 
        including method selection, number of samples, etc.
        
        Args:
            parent: The parent tree item (typically the Simulation object)
        """
        super().__init__(parent, icon="icons/XSimulatorUI/SolverSettings.ico")

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Solver Settings"

        self.enums = [e().__class__.__name__ for e in conf.SOLVERS]
        typ = XCore.PropertyEnum(
            self.enums,
            0,
        )
        typ.OnModified.Connect(self._update)
        self._properties.Add("type", typ)

        self.config = conf.SOLVERS[typ.Value]()
        draw_properties(self,self.config)

        asyncio.get_event_loop().call_soon(
            self._connect_signals
        )

    def _connect_signals(self) -> None:
        try:
            def description_changed(
                prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum
            ):
                if mod_type != XCore.kPropertyModified:
                    return

                self._notify_modified(True)
            
            solver_type_prop = self._properties.type
            assert isinstance(solver_type_prop, XCore.PropertyEnum)

            

            for prop in (self._properties.Description):
                assert isinstance(prop, XCore.Property)
                prop.OnModified.Connect(description_changed)
        except Exception as e:
            logger.debug(e)

    def _update(self, prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum):

        solver_value = self._properties.type.Value

        self._properties.Clear()
        typ = XCore.PropertyEnum(
            self.enums,
            solver_value,
        )
        #type.Value = material_value
        typ.OnModified.Connect(self._update)
        self._properties.Add("type", typ)
        for i in conf.SOLVERS:
            logger.debug(i)
            logger.debug(i())
            if typ.ValueDescription == i().__class__.__name__:
                self.config = i()
                
                draw_properties(self, self.config)
                break

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support for loading saved solver settings.
        
        Args:
            state: The serialized state to restore from
        """
        super().__setstate__(state)

    @property
    def description(self) -> str:
        """Gets the descriptive name of the solver settings as shown in the UI."""
        return self._properties.Description

    @description.setter
    def description(self, value: str) -> None:
        """Sets the descriptive name of the solver settings as shown in the UI."""
        self._properties.Description = value

    @property
    def properties(self) -> XCore.PropertyGroup:
        """
        Provides access to the property group containing solver configuration options.
        
        These properties will be displayed in the S4L properties panel when the
        solver settings are selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates that the solver settings are properly configured.
        
        Returns:
            True if the solver settings are valid, False otherwise
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
        Converts the solver settings to a suitable serializarion.

        
        Returns:
            A dictionary object with the solver setting parameters
        """

        output = {}
        output.update({"type": self._properties.type.ValueDescription})
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))

        return {"Solver_Settings": output}
