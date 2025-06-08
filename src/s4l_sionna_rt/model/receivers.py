import logging
from typing import TYPE_CHECKING

import XCore
import XCoreHeadless
import XCoreModeling as xm
from s4l_core.simulator_plugins.base.model.geometry_interface import HasGeometries
from s4l_core.simulator_plugins.base.model.group import Group
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties

if TYPE_CHECKING:
    from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem


logger = logging.getLogger(__name__)


class Receiver(HasGeometries):

    def __init__(
        self,
        parent: "TreeItem",
    ) -> None:
        """
        Initializes a receiver objects with default properties.
        
        Args:
            parent: The parent tree item (typically the Receivers collection)
        """
        allowed_types = self._get_allowed_entity_types()

        super().__init__(
            parent=parent,
            icon="icons/EmFdtdSimulatorUI/semx_pointsensor.ico",
            allowed_entity_types=allowed_types,
        )

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Receiver Settings"

        self.config = conf.create_Receiver()
        draw_properties(self,self.config)

    def _get_allowed_entity_types(self) -> tuple[type[xm.Entity], ...]:
        """
        Specifies which types of geometric entities can have receivers assigned to them.
        
        In this simulation, receivers can only be assigned to point entities (vertices)
        
        Returns:
            Tuple of allowed entity types (only Vertex objects in this case)
        """
        return (xm.Vertex,)

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
        Provides access to the property group containing parameters.
        
        These properties will be displayed in the S4L properties panel when this
        receiver is selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates that settings are complete.
        
        Returns:
            True if the receiiver settings are valid, False otherwise
        """
        if not (len(self._geometries) == 1 or len(self._geometries) == 0):
            return False

        return True

    def clear_status_recursively(self):
        """Clears any status indicators """
        self.clear_status()

    def as_api_model(self, prop_name, results_dir):
        """
        Serialize to appropriate format
        
        Returns:
            Dictionary serialization
        """
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        return {prop_name:output}


class Receivers(Group[Receiver]):
    """
    Collection class that manages a group of Receiver objects.
    
    This class provides functionality for adding, removing, and accessing
    individual receivers. It appears in the simulation tree as the
    "Receivers" node, which can be expanded to show individual receivers.
    """

    def __init__(
        self, parent: "TreeItem", is_expanded: bool = True, icon: str = ""
    ) -> None:
        """
        Initializes a new receivers collection.
        
        Args:
            parent: The parent tree item (typically the Simulation object)
            is_expanded: Whether the receivers node starts expanded in the UI tree
            icon: Optional custom icon path (defaults to standard sources icon)
        """
        super().__init__(
            parent,
            Receiver,
            is_expanded,
            icon="icons/EmFdtdSimulatorUI/semx_pointsensor.ico",
        )

    def _get_new_element_description(self) -> str:
        """
        Provides the base name used when creating new transmitters elements.
        
        Returns:
            The base description string used for new transmitters
        """
        return "Receiver"

    def clear_status_recursively(self):
        """
        Clears status indicators for this collection and all contained transmitter.
        
        This method is called before validation to ensure a clean slate for
        reporting any validation issues.
        """
        self.clear_status()
        for mat in self._elements:
            mat.clear_status_recursively()

    @property
    def description_text(self) -> str:
        """
        Gets the display text for this collection shown in the simulation tree.
        
        Returns:
            The plural form of the element type (e.g., "Receiver")
        """
        return f"Receivers"
