import logging
from typing import TYPE_CHECKING, cast

import s4l_sionna_rt.model.simulation as sim
from s4l_core.simulator_plugins.base.controller.simulation_binding_interface import (
    ISimulationBinding,
)

if TYPE_CHECKING:
    from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem

logger = logging.getLogger(__name__)


class SimulationBinding(ISimulationBinding):
    """
    Binding implementation that connects the simulation model to the UI tree structure.
    
    This class is responsible for defining how simulation components are represented
    in the S4L hierarchical UI tree and for navigating/retrieving items based on their 
    tree path.
    """

    @property
    def simulation(self) -> sim.Simulation:
        return cast("sim.Simulation", self._simulation)

    def count_children(self, path: list[int]) -> int:
        """
        Determines the number of child nodes at a specific tree path location.
        
        This method is essential for the UI to know how many child items to display
        at each level of the tree hierarchy. The path represents the numeric indices
        to navigate the tree structure.

        Args:
            path: The tree path as a list of integer indices

        Returns:
            Number of children at the specified path
        """
        simulation = self.simulation

        # Standard structure
        if len(path) == 2:  # Top level simulation node showing settings categories
            return 5  # Setup, Render, Materials, Antenna, Solver

        if len(path) == 3:
            if path[2] in (0, 1, 4):  # Setup, Render, Solver
                return 0  # these settings have no children
            elif path[2] == 2:
                return len(simulation.material_settings.elements) + 1
            elif path[2] == 3:
                return 2
            else:
                raise RuntimeError(f"Invalid path: {path}")

        if len(path) == 4:  
            if path[2] == 2 and path[3] == 0:
                return 0
            elif path[2] == 2 and path[3]>0:  
                return len(
                    simulation.material_settings.elements[int(path[3] - 1)].geometries
                )
            if path[2] == 3 and path[3] == 0:  
                return len(simulation.antenna.transmitters.elements)
            if path[2] == 3 and path[3] == 1:  
                return len(simulation.antenna.receivers.elements)

        if len(path) == 5:
            if path[2] == 3 and path[3] == 0: 
                return len(simulation.antenna.transmitters.elements[int(path[4])].geometries)
            if path[2] == 3 and path[3] == 1: 
                return len(simulation.antenna.receivers.elements[int(path[4])].geometries)

        return 0

    def get_tree_item(self, path: list[int]) -> "TreeItem | None":
        """
        Retrieves the specific simulation component at the given tree path.
        
        This method navigates the simulation object hierarchy based on the provided path
        and returns the appropriate component (settings, material, antenna, etc.) that
        should be displayed at that location in the UI tree.

        Args:
            path: The tree path as a list of integer indices

        Returns:
            The tree item at the specified path or None if the path is invalid
        """
        simulation = self.simulation

        if len(path) == 2:
            return simulation

        if path[2] == 0:
            sim_child = simulation.setup_settings
        elif path[2] == 1:
            sim_child = simulation.render_settings
        elif path[2] == 2:
            sim_child = simulation.material_settings
        elif path[2] == 3:
            sim_child = simulation.antenna
        elif path[2] == 4:
            sim_child = simulation.solver_settings
        else:
            logger.error(f"Invalid index for simulation child: {path[2]}")
            return None

        if len(path) == 3:
            return sim_child

        if len(path) == 4:
            if path[2] == 2 and path[3]==0: 
                return simulation.background_scene
            elif path[2] == 2 and path[3]>0:
                return simulation.material_settings.elements[path[3] -1]
            if path[2] == 3 and path[3]==0: 
                return simulation.antenna.transmitters
            if path[2] == 3 and path[3]==1:  
                return simulation.antenna.receivers

        if len(path) == 5:  # a geometry
            if path[2] == 2 and path[3] > 0: 
                return simulation.material_settings.elements[int(path[3] -1)].geometries[
                    int(path[4])
                ]
            if path[2] == 3 and path[3]==1: 
                return simulation.antenna.receivers.elements[int(path[4])]
            if path[2] == 3 and path[3]==0: 
                return simulation.antenna.transmitters.elements[int(path[4])]
            
        
        if len(path) == 6:
            if path[2] == 3 and path[3]==0: 
                return simulation.antenna.transmitters.elements[int(path[4])].geometries[
                    int(path[5])
                ]
            elif path[2] == 3 and path[3]==1:  
                return simulation.antenna.receivers.elements[int(path[4])].geometries[
                    int(path[5])
                ]
        

        return None
