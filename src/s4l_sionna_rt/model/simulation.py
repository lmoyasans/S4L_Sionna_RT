import logging
from typing import TYPE_CHECKING
import asyncio

import s4l_sionna_rt.model.render_settings as render_settings
import s4l_sionna_rt.model.material_settings as material_settings
import s4l_sionna_rt.model.setup_settings as setup_settings
import s4l_sionna_rt.model.solver_settings as solver_settings
import s4l_sionna_rt.model.antenna as antenna
import XPostProPython as pp
import XCore as xc
from s4l_core.simulator_plugins.base.model.help import create_help_button, display_help
from s4l_core.simulator_plugins.base.model.simulation_base import SimulationBase
from s4l_core.simulator_plugins.base.solver.project_runner import SolverBackend, config_type_t
import s4l_sionna_rt.model.background_scene as background_scene
from s4l_sionna_rt.solver.driver import api_models

if TYPE_CHECKING:
    from s4l_core.simulator_plugins.base.model.controller_interface import TreeItem

logger = logging.getLogger(__name__)

domain_id_map_t = dict[str, int]  # map from uuid (as str) to the domain id


class Simulation(SimulationBase):
    """
    Central model class representing a Sionna RT simulation.
    
    This class serves as the main container for all simulation settings and components,
    including setup parameters, render parameters, material properties, antennas, band solver parameters. 
    It provides methods for validating the simulation configuration and converting the model 
    to a format suitable for the solver.
    """

    @classmethod
    def get_simulation_type_name(cls) -> str:
        """
        Returns the display name used to identify this simulation type in the S4L interface.
        
        This name appears in the UI when users are selecting which type of simulation to create.
        """
        return "Sionna RT"

    @classmethod
    def get_simulation_description(cls) -> str:
        """
        Returns a brief description of what this simulation type does.
        
        This description appears in the UI to help users understand the purpose of this
        simulation type.
        """
        return "A simulation plugin for S4L"

    @classmethod
    def get_simulation_icon(cls) -> str:
        """
        Returns the path to the icon used to represent this simulation type in the UI.
        """
        return "icons/XSimulatorUI/new_simulation.ico"

    def __init__(
        self,
        parent: "TreeItem",
        sim_desc: str = "Simulation",
        sim_notes: str = "Solves for the radio propagation maps",
    ) -> None:
        """
        Initializes a new simulation instance with default settings.
        
        Creates a help button in the properties panel and schedules the connection
        of the help button event handler.
        
        Args:
            parent: The parent tree item
            sim_desc: A brief description of this specific simulation instance
            sim_notes: Additional notes about this simulation (default shows the equation)
        """
        super().__init__(parent, sim_desc, sim_notes)

        self._properties.Add("help_button", create_help_button())

        asyncio.get_event_loop().call_soon(self._connect_help)

    def on_initialize_settings(self) -> None:
        """
        Creates all the settings objects for this simulation.
        
        This method is called during initialization to set up the various settings 
        components that make up the simulation (setup, materials, antennas, render settings, etc.).
        Each component is responsible for a specific aspect of the simulation configuration.
        """
        self._setup_settings = setup_settings.SetupSettings(self)
        self._render_settings = render_settings.RenderSettings(self)
        self._material_settings = material_settings.Materials(self)
        self._background_scene = background_scene.BackgroundScene(self)
        self._antenna = antenna.Antennas(self)
        self._solver_settings = solver_settings.SolverSettings(self)

    def _connect_help(self):
        """
        Connects the help button click event to the help display handler.
        
        This method is scheduled to run soon after initialization to ensure the
        help button property is properly set up before connecting the event handler.
        """
        help_button = self._properties.help_button
        assert isinstance(help_button, xc.PropertyPushButton)
        help_button.OnClicked.Connect(self._display_help)

    def _display_help(self) -> None:
        """
        Displays help information about this simulation type when the help button is clicked.
        
        Shows a dialog with the simulation type title and a basic description of what
        the simulation does and how it works.
        """
        sim_type = "Sionna RT"
        title = f"{sim_type} Simulation"
        text = (
            f"This simulation solves the {sim_type} simulation"
            "\n\n"
            "For more information, please refer to the documentation."
        )
        display_help(title, text)

    @property
    def setup_settings(self) -> setup_settings.SetupSettings:
        return self._setup_settings

    @property
    def background_scene(self) -> background_scene.BackgroundScene:
        return self._background_scene


    @property
    def render_settings(self) -> render_settings.RenderSettings:
        return self._render_settings

    @property
    def material_settings(self) -> material_settings.Materials:
        return self._material_settings

    @property
    def antenna(self) -> antenna.Antennas:
        return self._antenna

    @property
    def solver_settings(self) -> solver_settings.SolverSettings:
        return self._solver_settings

    def register_extractor(self) -> pp.PythonModuleAlgorithm:
        """
        Registers a post-processing extractor for simulation results.
        
        This method is called by the S4L framework to set up result extraction and
        visualization capabilities for this simulation type.
        
        Returns:
            A PostPro algorithm that can extract and process simulation results
        """
        return pp.PythonModuleAlgorithm(
            "s4l_sionna_rt.model.simulation_extractor",
            0,
            1,
        )

    def solver_backend(self) -> tuple[SolverBackend, config_type_t | None]:
        """
        Specifies which type of solver backend to use for running this simulation.
        
        This method determines how the solver will be executed (as a process, thread, etc.)
        and any configuration needed for that execution mode.
        
        Returns:
            A tuple containing the solver backend type and optional configuration
        """
        return SolverBackend.PROCESS, None
    
    def get_solver_src(self) -> str:
        """
        Returns the Python module path to the solver implementation.
        
        The S4L framework uses this to locate and load the solver code when
        running a simulation of this type.
        
        Returns:
            The fully qualified module name for the solver implementation
        """
        return "s4l_sionna_rt.solver.driver"

    def clear_status_recursively(self) -> None:
        """
        Clears status indicators for this simulation and its components.
        
        This method is typically called before validation to ensure a clean
        slate for reporting validation issues.
        """
        super().clear_status_recursively()
        self.solver_settings.clear_status()
        self.antenna._transmitters.clear_status()
        self._setup_settings.clear_status()
        self._material_settings.clear_status()
        self._render_settings.clear_status()
        self._background_scene.clear_status()

    def validate(self) -> bool:
        """
        Validates that the simulation configuration is complete and ready to run.
        
        Performs checks to ensure all required settings are provided and within
        acceptable ranges. Sets status indicators to highlight any issues found.
        
        Returns:
            True if the simulation is valid and ready to run, False otherwise
        """
        self.clear_status_recursively()

        validation =  self._antenna.validate() and self._setup_settings.validate() and self._render_settings.validate() and self._material_settings.validate() and self._background_scene.validate() and self._solver_settings.validate()

        if not validation:
            return False

        return True

    def as_api_model(self) -> api_models.SimulationOutput:
        """
        Converts the simulation model to a format suitable for the solver API.
        
        This method transforms the UI-oriented model objects into a simplified
        representation that can be passed to the simulation solver. It validates
        the simulation first to ensure it is ready to run.
        
        Returns:
            A solver API model representation of this simulation
            
        Raises:
            RuntimeError: If validation fails
        """
        if not self.validate():
            raise RuntimeError("Validation failed")

        output = {}

        output.update(self._setup_settings.as_api_model(self.results_dir))
        output.update(self._render_settings.as_api_model(self.results_dir))
        mats = {}
        for num, mat in enumerate(self._material_settings.elements):
            mats.update(mat.as_api_model("mat_" + str(num), str(self.results_dir)))
        output.update({"Materials":mats})
        output.update(self._antenna.as_api_model(self.results_dir))
        output.update(self._solver_settings.as_api_model(self.results_dir))
        output.update(self._background_scene.as_api_model(self.results_dir))

        return api_models.SimulationOutput(
            scene=output
        )
