import logging
from typing import cast

from s4l_core.simulator_plugins.base.controller.simulation_binding_interface import (
    ISimulationBinding,
)
from s4l_core.simulator_plugins.base.controller.simulation_manager_interface import (
    ISimulationManager,
)
from s4l_core.simulator_plugins.base.model.simulation_base import SimulationBase
from s4l_core.simulator_plugins.common.registry import PluginRegistry
from s4l_sionna_rt.controller.simulation_binding import (
    SimulationBinding,
)
from s4l_sionna_rt.controller.simulation_manager import (
    SimulationManager,
)
from s4l_sionna_rt.model.simulation import (
    Simulation,
)

logger = logging.getLogger(__name__)


def create_binding(simulation: SimulationBase) -> ISimulationBinding:
    """
    Factory function that creates a binding between the simulation model and UI.
    
    This function is called by the S4L framework when a simulation of this type
    is created and needs to be displayed in the UI. It instantiates a SimulationBinding
    object that handles the tree structure representation of the simulation.
    
    Args:
        simulation: The base simulation instance to create a binding for
        
    Returns:
        A concrete SimulationBinding implementation for this simulation type
    """
    return SimulationBinding(cast(Simulation, simulation))


def create_manager(simulation: SimulationBase) -> ISimulationManager:
    """
    Factory function that creates a manager for handling UI interactions.
    
    This function is called by the S4L framework when a simulation of this type
    is created and needs UI management. It instantiates a SimulationManager object
    that provides actions and property displays for the simulation components.
    
    Args:
        simulation: The base simulation instance to create a manager for
        
    Returns:
        A concrete SimulationManager implementation for this simulation type
    """
    return SimulationManager(cast(Simulation, simulation))


def register():
    """
    Registers all simulation components with the S4L plugin system.
    
    This function is the main entry point for the plugin and is called by S4L during startup
    to register the simulation type, binding factory, and manager factory. This makes
    the plugin available in the S4L user interface and allows users to create simulations
    of this type.
    """
    logger.info("Registering Sionna RT Plugin...")

    # Register the simulation type
    PluginRegistry.register_simulation(Simulation)

    # Register binding factory
    sim_type = Simulation.get_simulation_type_name()
    PluginRegistry.register_binding_factory(sim_type, create_binding)

    # Register manager factory
    PluginRegistry.register_manager_factory(sim_type, create_manager)

    logger.info("Registered Sionna RT Plugin components successfully")
