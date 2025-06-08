import logging
from typing import TYPE_CHECKING
from typing_extensions import override

import XCore
import XCoreHeadless
import XCoreModeling as xm
from s4l_core.simulator_plugins.base.model.geometry_interface import HasGeometries
from s4l_core.simulator_plugins.base.model.group import Group
from s4l_sionna_rt.solver.driver import api_models as conf
from .draw import draw_properties
import asyncio

if TYPE_CHECKING:
    from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem


logger = logging.getLogger(__name__)


class MaterialSettings(HasGeometries):
    """
    Defines material properties that can be assigned to geometric entities in the simulation.
    
    This class represents a material with physical properties
    that can be assigned to one or more geometric meshes in the simulation domain. It inherits
    from HasGeometries to provide the ability to associate geometry with the material.
    """


    def __init__(
        self,
        parent: "TreeItem",
    ) -> None:
        """
        Initializes a new material settings object with default properties.
        
        Creates the properties panel for this material with appropriate controls
        for setting physical parameters.
        
        Args:
            parent: The parent tree item (typically the Materials collection)
        """
        allowed_types = self._get_allowed_entity_types()

        super().__init__(parent=parent, allowed_entity_types=allowed_types)

        self.enums = [e().__class__.__name__ for e in conf.MATERIAL_TYPES]
        typ = XCore.PropertyEnum(
            self.enums,
            0,
        )
        typ.OnModified.Connect(self._update)

        self._properties = XCoreHeadless.DialogOptions()
        self._properties.Description = "Material Settings"

        self._properties.Add("type",typ)

        self.config = conf.MATERIAL_TYPES[typ.Value]()
        draw_properties(self,self.config)

        asyncio.get_event_loop().call_soon(
            self._connect_signals
        )

    def _connect_signals(self) -> None:
        def description_changed(
            prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum
        ):
            if mod_type != XCore.kPropertyModified:
                return

            self._notify_modified(True)
        
        material_type_prop = self._properties.type
        assert isinstance(material_type_prop, XCore.PropertyEnum)

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

        


    def _update(self, prop: XCore.Property, mod_type: XCore.PropertyModificationTypeEnum):

        material_value = self._properties.type.Value
        self._properties.Clear()
        typ = XCore.PropertyEnum(
            self.enums,
            material_value,
        )
        #type.Value = material_value
        typ.OnModified.Connect(self._update)
        self._properties.Add("type", typ)

        for i in conf.MATERIAL_TYPES:
            logger.debug(i)
            logger.debug(i())
            if typ.ValueDescription == i().__class__.__name__:
                self.config = i()
                
                draw_properties(self, self.config)
                break

        


    def _get_allowed_entity_types(self) -> tuple[type[xm.Entity], ...]:
        """
        Specifies which types of geometric entities can have this material assigned to them.
        
        In this simulation, materials can only be assigned to solid bodies (not surfaces
        or other entity types). This constraint ensures proper physical modeling.
        
        Returns:
            Tuple of allowed entity types (only Body objects in this case)
        """
        return (xm.TriangleMesh,)

    def __setstate__(self, state) -> None:
        super().__setstate__(state)

    @property
    def description(self) -> str:
        return self._properties.Description

    @description.setter
    def description(self, value: str) -> None:
        self._properties.Description = value

    @property
    def properties(self) -> XCore.PropertyGroup:
        """
        Provides access to the property group containing editable material properties.
        
        These properties will be displayed in the S4L properties panel when this
        material is selected in the UI.
        """
        return self._properties

    def validate(self) -> bool:
        """
        Validates that the material settings are complete
        
        Returns:
            True if the material settings are valid, False otherwise
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

    def clear_status_recursively(self):
        """Clears any status indicators for this material."""
        self.clear_status()

    def store_geometry(self, entity_id, results_dir):
        """
        Storage of the triangular meshes of the imported and/or modelled 
        geometries in the correct format
        """
        entity_file = entity_id + ".ply"
        entity = xm.GetActiveModel().LookupEntity(XCore.Uuid(entity_id))
        with open(results_dir + "/input_files/" + entity_file, "w") as f:

            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {entity.Points.shape[0]}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write(f"element face {entity.Triangles.shape[0]}\n")
            f.write("property list uchar uint vertex_indices\n")
            f.write("end_header\n")

            for i in range(entity.Points.shape[0]):
                f.write(f"{entity.Points[i][0]} {entity.Points[i][1]} {entity.Points[i][2]}\n")

            for i in range(entity.Triangles.shape[0]):
                f.write(f"3 {entity.Triangles[i][0]} {entity.Triangles[i][1]} {entity.Triangles[i][2]}\n")
        return "input_files/" + entity_file

    def as_api_model(self, prop_name, results_dir):
        """
        Converts this material settings object to dictionary format 
        for posterior JSON serialization.
        
        Returns:
            A MaterialSettings serialized in dictionary format
        """

        output = {}
        output.update({"type": self._properties.type.ValueDescription})
        for i in self.config.__dict__.keys():
            output.update(self.config.__dict__[i].to_format(i, results_dir))
        geoms = []
        for geom in self.geometries:
            geom_file = self.store_geometry(geom.entity_id, results_dir)
            geoms.append({"fname":str(geom_file), "name":geom.description})
        output.update({"geometries": geoms})
        return {prop_name: output}


class Materials(Group[MaterialSettings]):
    """
    Collection class that manages a group of MaterialSettings objects.
    
    This class provides functionality for adding, removing, and accessing
    individual material settings. It appears in the simulation tree as the
    "Materials" node, which can be expanded to show individual materials.
    """

    def __init__(
        self, parent: "TreeItem", is_expanded: bool = True, icon: str = ""
    ) -> None:
        """
        Initializes a new materials collection.
        
        Args:
            parent: The parent tree item (typically the Simulation object)
            is_expanded: Whether the materials node starts expanded in the UI tree
            icon: Optional custom icon path (defaults to standard materials icon)
        """
        super().__init__(
            parent,
            MaterialSettings,
            is_expanded,
            icon="icons/XMaterials/materials.ico",
        )

    def validate(self):
        for elem in self.elements:
            if not elem.validate():
                return False
        return True

    def _get_new_element_description(self) -> str:
        """
        Provides the base name used when creating new material elements.
        
        Returns:
            The base description string used for new materials
        """
        return "Material"

    def clear_status_recursively(self):
        """
        Clears status indicators for this collection and all contained materials.
        
        This method is called before validation to ensure a clean slate for
        reporting any validation issues.
        """
        self.clear_status()
        for mat in self._elements:
            mat.clear_status_recursively()
        
    def check_geometry(self, entity_id):
        for mat in self.elements:
            for geometry in mat._geometries:
                if geometry.entity_id == entity_id:
                    return False
        return True


    @property
    def description_text(self) -> str:
        """
        Gets the display text for this collection shown in the simulation tree.
        
        Returns:
            The plural form of the element type (e.g., "Materials")
        """
        return f"Materials"