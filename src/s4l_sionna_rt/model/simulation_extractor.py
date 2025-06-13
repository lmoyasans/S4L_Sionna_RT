#!python3


import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
import asyncio
import s4l_sionna_rt.solver.driver.api_models as mdl
import s4l_core.simulator_plugins.common.plugin_plot_manager as ppm
import s4l_sionna_rt.model.plots as plots_functions
import XCore as xc
import XPostProcessor as xp
import XPostProPython as pp
import numpy as np

FILENAME_SUFFIX = ".vtr"
JSON_OUTPUT = "summary.json"

logger = logging.getLogger(__name__)


"""
Class Hierarchy for Simulation Extraction:

                            Has A                         Has A                           Has A
  ┌───────────────────────┐        ┌────────────────────┐        ┌──────────────────────┐          ┌──────────────────┐
  │ PythonModuleAlgorithm ├───────►│   AlgorithmImpl    ├───────►├ SimulationExtractor  ├─────────►│ IExtractorParent │
  │      (C++)            │        │      (Python)      │        │       Impl           │          │                  │
  └───────────────────────┘        └────────────────────┘        └──────────────────────┘          └──────────────────┘



  ┌───────────────┐     Is A     ┌──────────────────┐
  │ AlgorithmImpl ├─────────────►│ IExtractorParent │
  └───────────────┘              └──────────────────┘

"""


class IExtractorParent(ABC):
    """
    The interface for the parent of a simulation extractor for a
    particular simulation type.  It provides the child info about the simulation
    being extracted and allows for the addition of settings and output
    ports to the parent algorithm.
    """

    @abstractmethod
    def add_property(self, name: str, property: xc.Property) -> xc.Property:
        """
        Add a property to the parent C++ class for use in the settings
        n.b. checks that this property is not already present to avoid
        an overwrite during de-serialisation.
        """
        ...

    @property
    @abstractmethod
    def input_simulation(self) -> mdl.SimulationOutput:
        """
        Get the simulation being extracted by this extractor
        """
        ...

    @property
    @abstractmethod
    def output_files_dir(self) -> Path:
        """
        Get the directory containing the output files being extracted from
        by this extractor
        """
        ...

    @abstractmethod
    def ResizeNumberOfOutputPorts(self, num_outputs: int) -> None:
        """
        Set the number of output ports
        """
        ...


class SimulationExtractorImpl:
    """
    Implementation of the simulation results extractor.
    
    This class processes the output files generated and makes them available for
    visualization and analysis in the S4L post-processing environment.
    """

    def __init__(self, parent: "IExtractorParent") -> None:
        """
        Initializes the simulation extractor with references to the parent algorithm.
        
        Sets up empty collections for outputs and extractors that will be populated
        during the extraction process.
        
        Args:
            parent: The parent algorithm that provides access to output files
        """
        super().__init__()
        self._parent = parent
        self._outputs: list[xp.DataObject | None] = []
        self._extractors: list[xp.VtkFieldImporter] = []
        self.json_data: dict = {}

    def _load_json_data(self, filepath: Path):
        """
        Loads simulation summary data from a JSON file into a data object.
        
        Reads from the JSON file and creates a structured data object that 
        can be displayed in the post-processor.
        
        Args:
            filepath: Path to the summary JSON file
            
        Returns:
            A dictionary containing the structured summary data
        """
        with open(filepath) as fh:
            self.json_data = json.load(fh)
        return self.json_data

    def DoCheckInputConnections(self, inputs: list[xp.AlgorithmOutput]) -> bool:
        """
        Checks that input connections to this algorithm are valid.
        
        For this extractor, no inputs are expected as it reads directly from
        result files rather than connecting to other algorithm outputs.
        
        Args:
            inputs: List of input connections
            
        Returns:
            True if the inputs are valid (empty list in this case)
        """
        return len(inputs) == 0

    def DoComputeOutputAttributes(self, child) -> bool:
        """
        Sets up the extractors and computes output attributes for all fields.
        
        This method is called during the preparation phase of the algorithm execution.
        It creates VTK importers for each field, configures output ports, and
        loads the summary JSON data.
        
        Returns:
            True if the attributes were computed successfully
        """
        num_outputs = 1
        self._parent.ResizeNumberOfOutputPorts(num_outputs)

        # Update attributes for all extractors

        self._load_json_data(self._parent.output_files_dir / JSON_OUTPUT)

        self._outputs = [None] * (num_outputs)
        self._update_outputs(child)
        return True

    def define_child_properties(self,child,json_data):

        """
        Defines the GUI parameters that are going to be shown 
        in the AlgorithmImplementation child, depending on the 
        type of solver used for the simulation
        """

        plot_types =json_data["type"]

        # Plots
        plots_group = child.add_property("plots", xc.PropertyGroup())
        assert isinstance(plots_group, xc.PropertyGroup)

        child.plots_group = plots_group

        if plot_types == "RadioMap":
            plots_group.Description = "RadioMap solver results"
            options = ["SINR", "Path gain", "RSS", "Image"]
            options_tr = [f"Transmitter {e}" for e in np.linspace(0,np.array(json_data["sinr"]).shape[0], np.array(json_data["sinr"]).shape[0],dtype=int)]
            prop = plots_group.Add("ind", xc.PropertyEnum(options_tr,0))
            prop.Description = "Select transmitter"
            child.index_selector = prop

        else:
            try:
                plots_group.Description = "Paths solver results"
                options = ["Channel frequency response", "Channel Impulse response (histogram)", "Channel Impulse response", "Discrete channel taps", "Image"]
                options_tr =[f"Transmitter {e}" for e in np.linspace(0,np.array(json_data["h_freq"]).shape[0], np.array(json_data["h_freq"]).shape[0],dtype=int)]
                prop = plots_group.Add("ind", xc.PropertyEnum(options_tr,0))
                prop.Description = "Select transmitter"
                child.index_selector = prop
                options_tr =[f"TX_ant {e}" for e in np.linspace(0,np.array(json_data["h_freq"]).shape[1], np.array(json_data["h_freq"]).shape[1],dtype=int)]
                prop = plots_group.Add("ind2", xc.PropertyEnum(options_tr,0))
                prop.Description = "Select tx_ant"
                child.index_selector2 = prop
                options_tr =[f"Receiver {e}" for e in np.linspace(0,np.array(json_data["h_freq"]).shape[2], np.array(json_data["h_freq"]).shape[2],dtype=int)]
                prop = plots_group.Add("ind3", xc.PropertyEnum(options_tr,0))
                prop.Description = "Select receiver"
                child.index_selector3 = prop
                options_tr =[f"RX_ant {e}" for e in np.linspace(0,np.array(json_data["h_freq"]).shape[3], np.array(json_data["h_freq"]).shape[3],dtype=int)]
                prop = plots_group.Add("ind4", xc.PropertyEnum(options_tr,0))
                prop.Description = "Select rx_ant"
                child.index_selector4 = prop
                options_tr =[f"Timestep {e}" for e in np.linspace(0,np.array(json_data["h_freq"]).shape[4], np.array(json_data["h_freq"]).shape[4],dtype=int)]
                prop = plots_group.Add("ind5", xc.PropertyEnum(options_tr,0))
                prop.Description = "Select time step"
                child.index_selector5 = prop
            except Exception as e:
                logger.error(e)
            

        self.Icon = "icons/XPostProcessor/field_extractor.ico"

        prop = plots_group.Add("plots_dropd", xc.PropertyEnum(
            options,
            0,
        ))
        prop.Description = "Select plot"
        child.plot_selector_prop = prop


        prop = plots_group.Add("show_plot", xc.PropertyPushButton())
        prop.Description = "Show Plot"
        child.show_plot_prop = prop

        # connect not right away, but after the seriazliation
        asyncio.get_event_loop().call_soon(
            child._connect_signals
        )



    def _update_outputs(self,child) -> None:
        """
        Updates the cached output data objects with current extractor results.
        
        Collects field data from all extractors and updates the output cache
        to ensure the latest data is available when requested by the post-processor.
        """
        num_outputs = len(self._extractors) + 1
        # assert len(self.FIELD_NAMES) == num_outputs - 1
        assert len(self._outputs) == num_outputs

        # TODO: there is not yet a proper DataObject for plotly json
        # self._outputs[num_outputs - 1] = self.json_data
        self.define_child_properties(child, self.json_data)


    def DoComputeOutputData(self, child, index: int) -> bool:
        """
        Computes the output data for a specific output port.
        
        Triggers computation in all extractors and updates the output cache.
        This method is called when the post-processor needs data from a specific
        output port.
        
        Args:
            index: The index of the output port to compute
            
        Returns:
            True if the computation was successful
        """

        self._update_outputs(child)
        return True

    def GetOutputDataObject(self, child, output_index: int = 0) -> xp.DataObject:
        """
        Retrieves the data object for a specific output port.
        
        Returns the appropriate field data or summary data based on the
        requested output index. Ensures outputs are computed if they
        haven't been already.
        
        Args:
            output_index: The index of the output port to get data from
            
        Returns:
            The data object for the specified output port
        """
        if not self._outputs:
            self.DoComputeOutputAttributes(child)

        output = self._outputs[output_index]
        
        return output if output is not None else xp.FloatFieldData()


class AlgorithmImpl(IExtractorParent):
    """
    Python-side implementation of the S4L post-processor algorithm for result extraction.
    
    This class bridges between the C++ PythonModuleAlgorithm and the Python-based
    SimulationExtractorImpl. It handles properties, input/output management, and
    delegates the actual extraction work to SimulationExtractorImpl.
    """

    def __init__(self, parent: pp.PythonModuleAlgorithm) -> None:
        """
        Initializes the algorithm implementation with a reference to the parent C++ algorithm.
        
        Sets up the UI properties and configures the parent algorithm with basic settings.
        
        Args:
            parent: The C++ PythonModuleAlgorithm that hosts this implementation
        """
        super().__init__()

        self._extractor: SimulationExtractorImpl | None = None

        self._parent = parent
        self._parent.SetOneExecutionUpdatesAll(True)

        prop = self.add_property("results_dir", xc.PropertyString(""))
        prop.Description = "Results Dir."

        self.plots_group: xc.PropertyGroup = None
        self.plot_selector_prop: xc.PropertyEnum = None
        self.index_selector: xc.PropertyEnum = None
        self.index_selector2: xc.PropertyEnum = None
        self.index_selector3: xc.PropertyEnum = None
        self.index_selector4: xc.PropertyEnum = None
        self.index_selector5: xc.PropertyEnum = None
        self.show_plot_prop: xc.PropertyPushButton = None

        
        

    def _connect_signals(self) -> None:

        """
        Defines the behavior of the the visualization, generating the necessary 
        plots based on the parameters provided by the user in the UI
        """
        
        def show_plot():
            assert isinstance(self.plot_selector_prop, xc.PropertyEnum)
            plot_name = self.plot_selector_prop.ValueDescription
            if plot_name == "SINR":
                tr_index = self.index_selector.Value
                x = (np.linspace(0,np.array(np.array(self._extractor.json_data["sinr"])).shape[2], np.array(self._extractor.json_data["sinr"]).shape[2], dtype=int ))
                y = (np.linspace(0,np.array(self._extractor.json_data["sinr"]).shape[1], np.array(self._extractor.json_data["sinr"]).shape[1], dtype=int ))
                z_data = np.array(self._extractor.json_data["sinr"])[tr_index]
                plot_data = getattr(plots_functions, "generate_heatmap")(x,y,z_data, "SINR", "Signal-to-interference-plus-noise ratio [dB]")
            elif plot_name == "Path gain":
                tr_index = self.index_selector.Value
                x = (np.linspace(0,np.array(self._extractor.json_data["path_gain"]).shape[2], np.array(self._extractor.json_data["path_gain"]).shape[2], dtype=int ))
                y = (np.linspace(0,np.array(self._extractor.json_data["path_gain"]).shape[1], np.array(self._extractor.json_data["path_gain"]).shape[1], dtype=int ))
                z_data = np.array(self._extractor.json_data["path_gain"])[tr_index]
                plot_data = getattr(plots_functions, "generate_heatmap")(x,y,z_data, "Path gain", "Path_gain [dB]")
            elif plot_name == "RSS":
                tr_index = self.index_selector.Value
                x = (np.linspace(0,np.array(self._extractor.json_data["rss"]).shape[2], np.array(self._extractor.json_data["rss"]).shape[2], dtype=int ))
                y = (np.linspace(0,np.array(self._extractor.json_data["rss"]).shape[1], np.array(self._extractor.json_data["rss"]).shape[1],dtype=int ))
                z_data = np.array(self._extractor.json_data["rss"])[tr_index]
                plot_data = getattr(plots_functions, "generate_heatmap")(x,y,z_data, "RSS","Received signal strength(RSS) [dBm]")
            elif plot_name == "Image":
                plot_data = getattr(plots_functions, "generate_image")(self._extractor.json_data["image"], "Rendered scene")
            elif plot_name =="Channel frequency response":
                ind1 = self.index_selector.Value
                ind2 = self.index_selector2.Value
                ind3 = self.index_selector3.Value
                ind4 = self.index_selector4.Value
                ind5 = self.index_selector5.Value
                plot_data = getattr(plots_functions, "generate_line_plot")(self._extractor.json_data["h_freq"][ind1][ind2][ind3][ind4][ind5], "Subcarrier index","|h_freq|", "Channel frequency response")
            elif plot_name =="Discrete channel taps":
                ind1 = self.index_selector.Value
                ind2 = self.index_selector2.Value
                ind3 = self.index_selector3.Value
                ind4 = self.index_selector4.Value
                ind5 = self.index_selector5.Value
                taps_selected=self._extractor.json_data["taps"][ind1][ind2][ind3][ind4][ind5]
                taps_complex = np.array([complex(d['real'], d['imag']) for d in taps_selected])
                taps = np.abs(taps_complex)
                plot_data = getattr(plots_functions, "generate_discrete_scatter_plot")(taps)
            elif plot_name == "Channel Impulse response (histogram)":
                ind1 = self.index_selector.Value
                ind2 = self.index_selector2.Value
                ind3 = self.index_selector3.Value
                ind4 = self.index_selector4.Value
                ind5 = self.index_selector5.Value
                a_selected = self._extractor.json_data["a"][ind1][ind2][ind3][ind4]
                a = [a[ind5] for a in a_selected]
                a_complex = np.array([complex(d['real'], d['imag']) for d in a])
                a_abs = np.abs(a_complex)
                tau_selected = np.array(self._extractor.json_data["tau"][ind1][ind2][ind3][ind4])
                bins = np.linspace(tau_selected.min(), tau_selected.max(), 20)
                hist, bin_edges = np.histogram(tau_selected, bins=bins, weights=a_abs)
                plot_data = getattr(plots_functions, "generate_cir_binned_histogram")(bin_edges, hist)
            elif plot_name == "Channel Impulse response":
                ind1 = self.index_selector.Value
                ind2 = self.index_selector2.Value
                ind3 = self.index_selector3.Value
                ind4 = self.index_selector4.Value
                ind5 = self.index_selector5.Value
                a_selected = self._extractor.json_data["a"][ind1][ind2][ind3][ind4]
                a = [a[ind5] for a in a_selected]
                a_complex = np.array([complex(d['real'], d['imag']) for d in a])
                a_abs = np.abs(a_complex)
                tau_selected = np.array(self._extractor.json_data["tau"][ind1][ind2][ind3][ind4])
                plot_data = getattr(plots_functions, "generate_discrete_scatter_plot")(a_abs, tau_selected, title="Channel Impulse response", name="tau vs a", xaxis="Tau [ns]", yaxis="|a|")
            ppm.create_plot(plot_data)
            
                
        assert isinstance(self.show_plot_prop, xc.PropertyPushButton)
        self.show_plot_prop.OnClicked.Connect(show_plot)



    def add_property(self, name: str, property: xc.Property) -> xc.Property:
        """
        Adds a property to the parent algorithm, avoiding overwriting existing properties.
        
        This method is used to add UI-configurable properties to the algorithm,
        checking first if the property already exists (which might happen during
        deserialization).
        
        Args:
            name: The name of the property to add
            property: The property object to add
            
        Returns:
            The added or existing property
        """
        if (
            existing_prop := self._parent.FindChild(name)
        ) is None:  # make sure we don't overwrite a deserialized property
            return self._parent.Add(name, property)
        else:
            assert isinstance(existing_prop, xc.Property)
            return existing_prop

    def _results_dir(self) -> Path:
        """
        Retrieves the results directory path from the properties.
        
        Attempts to resolve the configured results directory path, checking for
        both absolute and relative paths (relative to the current document).
        
        Returns:
            The resolved path to the results directory
            
        Raises:
            RuntimeError: If the results directory cannot be found
        """
        if (results_dir_prop := self._parent.FindChild("results_dir")) is None:
            raise RuntimeError("Failed to find results_dir child")

        assert isinstance(results_dir_prop, xc.PropertyString)

        assert len(results_dir_prop.Value) > 0, "Results dir was not set"

        stored_path = Path(results_dir_prop.Value)
        if stored_path.is_dir():
            results_path = stored_path
        else:  # perhaps its is a path relative to the current smash file
            results_relpath = Path(results_dir_prop.Value)

            app = xc.GetApp()
            doc = app.Document

            results_path = Path(doc.FileFolder) / results_relpath
            if not results_path.is_dir():
                raise RuntimeError(
                    f"Failed to find results_dir, tried: {stored_path} and {results_path}"
                )

        return results_path

    def _input_filepath(self) -> Path:
        """
        Determines the path to the input file used for the simulation.
        
        Locates the original input file in the expected location within the
        results directory structure.
        
        Returns:
            The path to the input JSON file
            
        Raises:
            ValueError: If the input file cannot be found
        """ 
    
        input_filepath = self._results_dir() / "input_files" / "input_file.json"
        if not input_filepath.is_file():
            raise ValueError(f"Could not find: {input_filepath}")

        return input_filepath

    @property
    def input_simulation(self) -> mdl.SimulationOutput:
        """
        Retrieves the simulation model from the input file.
        
        Loads and deserializes the original simulation model from the
        JSON input file used for the simulation run.
        
        Returns:
            The deserialized Simulation object
        """
        with open(self._input_filepath()) as fh:
            sim: mdl.Simulation = mdl.Simulation.schema().loads(fh.read())  # type: ignore
        return sim

    @property
    def output_files_dir(self) -> Path:
        """
        Provides the path to the directory containing simulation output files.
        
        Returns:
            The path to the output_files directory within the results folder
        """
        return self._results_dir() / "output_files"

    def ResizeNumberOfOutputPorts(self, num_outputs: int) -> None:
        """
        Adjusts the number of output ports on the parent algorithm.
        
        This method is called by the extractor implementation to configure
        the correct number of output ports for the available result fields.
        
        Args:
            num_outputs: The number of output ports to configure
        """
        self._parent.ResizeNumberOfOutputPorts(num_outputs)

    def DoCheckInputConnections(self, inputs: list[xp.AlgorithmOutput]) -> bool:
        """
        Validates the input connections to the algorithm.
        
        Delegates to the extractor implementation to check if the inputs
        are valid for this algorithm.
        
        Args:
            inputs: The list of input connections
            
        Returns:
            True if the inputs are valid
        """
        extractor = self._get_or_create_extractor()
        return extractor.DoCheckInputConnections(inputs)

    def DoComputeOutputAttributes(self) -> bool:
        """
        Prepares the output attributes for all algorithm outputs.
        
        Delegates to the extractor implementation to compute and configure
        all output attributes.
        
        Returns:
            True if the attributes were computed successfully
        """
        extractor = self._get_or_create_extractor()
        return extractor.DoComputeOutputAttributes(self)

    def DoComputeOutputData(self, index: int) -> bool:
        """
        Computes the output data for a specific output port.
        
        Delegates to the extractor implementation to compute the
        requested output data.
        
        Args:
            index: The index of the output port to compute
            
        Returns:
            True if the data was computed successfully
        """
        extractor = self._get_or_create_extractor()
        return extractor.DoComputeOutputData(self,index)

    def _get_or_create_extractor(self) -> "SimulationExtractorImpl":
        """
        Gets or creates the appropriate extractor implementation.
        
        Ensures that a simulation extractor instance exists and is of the
        correct type for the current simulation.
        
        Returns:
            The simulation extractor implementation
        """
        extractor_cls = SimulationExtractorImpl

        if not isinstance(self._extractor, extractor_cls):
            self._extractor = extractor_cls(self)

        return self._extractor

    def GetOutputDataObject(self, output_index: int = 0) -> xp.DataObject:
        """
        Retrieves the data object for a specific output port.
        
        Delegates to the extractor implementation to get the requested
        output data object.
        
        Args:
            output_index: The index of the output port to get data from
            
        Returns:
            The data object for the specified output port
        """
        extractor = self._get_or_create_extractor()
        return extractor.GetOutputDataObject(self, output_index)
