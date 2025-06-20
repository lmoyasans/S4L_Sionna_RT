import logging
from typing import TYPE_CHECKING

import XCore
import XCoreHeadless
import XCoreModeling as xm
from s4l_core.simulator_plugins.base.model.geometry_interface import HasGeometries
import s4l_v1 as s4l
from s4l_core.simulator_plugins.base.model.group import Group
from s4l_core.simulator_plugins.base.model.geometry import Geometry
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties
import asyncio
from typing_extensions import override

if TYPE_CHECKING:
    from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem


logger = logging.getLogger(__name__)


class Transmitter(HasGeometries):

    def __init__(
        self,
        parent: "TreeItem",
    ) -> None:
        """
        Initializes a transmitter with default properties.
        
        Args:
            parent: The parent tree item (typically the Transmitters collection)
        """
        allowed_types = self._get_allowed_entity_types()

        super().__init__(
            parent=parent,
            icon="icons/EmFdtdSimulatorUI/semx_pointsensor.ico",
            allowed_entity_types=allowed_types,
        )

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Transmitter Settings"

        self.config = conf.create_Transmitter()
        draw_properties(self,self.config)
        self._properties.position.OnModified.Connect(self._update)
        asyncio.get_event_loop().call_soon(
            self._connect_signals
        )


    def _get_allowed_entity_types(self) -> tuple[type[xm.Entity], ...]:
        """
        Specifies which types of geometric entities can have transmitters assigned to them.
        
        In this simulation, transmitters can only be assigned to point entities (vertices)
        
        Returns:
            Tuple of allowed entity types (only Vertex objects in this case)
        """
        return (xm.Vertex,)

    def _connect_signals(self) -> None:
        def description_changed(
            prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum
        ):
            if mod_type != XCore.kPropertyModified:
                return

            self._notify_modified(True)

    def _update(self, prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum):

        if prop.Description == "Position":
            if len(self._geometries)==1:
                entity = xm.GetActiveModel().LookupEntity(XCore.Uuid(self._geometries[0].entity_id))
                t = s4l.model.Transform()
                t.Translation = prop.Value - entity.Position
                entity.ApplyTransform(t)

    def change_position(self, prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum):
        entity = xm.GetActiveModel().LookupEntity(XCore.Uuid(self._geometries[0].entity_id))
        try:
            self._properties.position.Value = entity.Position
        except Exception as e:
            logger.error(e)

    @override
    def add_geometry(self, entity_id: str) -> bool:
        """
        Add a geometry with the given entity ID.

        Args:
            entity_id: The entity ID to add

        Returns:
            True if the geometry was added, False otherwise
        """
        if not self.can_add_geometry(entity_id):
            return False

        # Pass the allowed entity types to the geometry
        geometry = Geometry(self, entity_id, self._allowed_entity_types)
        entity = xm.GetActiveModel().LookupEntity(XCore.Uuid(geometry.entity_id))
        entity.Properties.OnChildModified.Connect(self.change_position)
        self._properties.position.Value = entity.Position
        color = XCore.Color(1,0.349,0.204,1)
        entity.Color = color
        self._geometries.append(geometry)
        self._notify_modified(True)
        return True

    def __setstate__(self, state) -> None:
        """
        Custom deserialization support .
        
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
        Provides access to the property group containing transmitter parameters.
        
        These properties will be displayed in the S4L properties panel when this
        transmitter is selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates that the transmitter settings are complete.
        
        Returns:
            True if the transmitter settings are valid, False otherwise
        """
        if not (len(self._geometries) == 1 or len(self._geometries) == 0):
            return False

        return True

    def clear_status_recursively(self):
        """Clears any status indicators for this receiver."""
        self.clear_status()

    def as_api_model(self, prop_name, results_dir):
        """
        Converts the transmitter object into the correct serialization
        
        Returns:
            A dict object with the transmitter parameters
        """
        output = {}
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        return {prop_name:output}

    @override
    def can_add_geometry(self, entity_id: str) -> bool:
        """
        Check if a geometry with the given entity ID can be added.

        Args:
            entity_id: The entity ID to check

        Returns:
            True if the entity is valid for the allowed types, False otherwise
        """
        entity = xm.GetActiveModel().LookupEntity(XCore.Uuid(entity_id))

        if not isinstance(entity, self._allowed_entity_types):
            return False

        # Check if entity is already added
        for geometry in self._geometries:
            if geometry.entity_id == entity_id:
                return False

        return self.parent.check_geometry(entity_id)


class Transmitters(Group[Transmitter]):
    """
    Collection class that manages a group of Transmitter objects.
    
    This class provides functionality for adding, removing, and accessing
    individual transmitters. It appears in the simulation tree as the
    "Transmitters" node, which can be expanded to show individual transmitters.
    """

    def __init__(
        self, parent: "TreeItem", is_expanded: bool = True, icon: str = ""
    ) -> None:
        """
        Initializes a new transmitters collection.
        
        Args:
            parent: The parent tree item (typically the Simulation object)
            is_expanded: Whether the transmitters node starts expanded in the UI tree
            icon: Optional custom icon path (defaults to standard sources icon)
        """
        super().__init__(
            parent,
            Transmitter,
            is_expanded,
            icon="icons/EmFdtdSimulatorUI/semx_pointsensor.ico",
        )

    def _get_new_element_description(self) -> str:
        """
        Provides the base name used when creating new transmitters elements.
        
        Returns:
            The base description string used for new transmitters
        """
        return "Transmitter"

    def clear_status_recursively(self):
        """
        Clears status indicators for this collection and all contained transmitters.
        
        This method is called before validation to ensure a clean slate for
        reporting any validation issues.
        """
        self.clear_status()
        for trs in self._elements:
            trs.clear_status_recursively()

    @property
    def description_text(self) -> str:
        """
        Gets the display text for this collection shown in the simulation tree.
        
        Returns:
            The plural form of the element type (e.g., "Transmitter")
        """

        return f"Transmitters"

    def check_geometry(self, entity_id):
        for trs in self.elements:
            for geometry in trs._geometries:
                if geometry.entity_id == entity_id:
                    return False
        return True
