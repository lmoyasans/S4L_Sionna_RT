from dataclasses import dataclass
from enum import Enum

from dataclasses_json import CatchAll,dataclass_json
from s4l_core.simulator_plugins.base.solver.driver.api_models import (
    ApiSimulationBase,
    BaseSimulations,
)
import s4l_sionna_rt.adapters as adp

"""
Define the dataclasses necesary for the automatic drawing of the parameters,
generating a dataclass that links to an instance of the properties that can
draw and serialize in a recursive way.

It also defines the necessary constants.
"""


IMAGE_FILTERS = (
    "EXR Files (*.exr)|*.exr|"
    "PNG Files (*.png;*.PNG)|*.png;*.PNG|"
    "JPEG Files (*.jpeg;*.jpg)|*.jpeg;*.jpg|"
    "BMP Files (*.bmp)|*.bmp|"
    "TGA Files (*.tga)|*.tga|"
    "All Image Files (*.exr;*.png;*.PNG;*.jpeg;*.jpg;*.bmp;*.tga)|*.exr;*.png;*.PNG;*.jpeg;*.jpg;*.bmp;*.tga|"
    )

PY_FILTERS = ("Python Files (*.py)|*.py|")

ITU_MATERIALS = ["concrete", "brick", "plasterboard", "wood", "glass", "ceiling_board", "chipboard", "plywood", "marble", "floorboard",  "metal", "very_dry_ground", "medium_dry_ground", "wet_ground"]
SCATTERING_PATTERNS = ["lambertian", "directive", "backscattering", "custom"]
SCATTERING_PATTERNS_CLASSES = [adp.Base(), adp.Base(), adp.Base(), adp.File(PY_FILTERS)]
SCATTERING_PATTERNS_PROPNAMES = ["", "", "", "Select factory source file:"]
ANTENNA_PATTERNS = ["iso", "dipole", "hw_dipole", "tr38901", "custom"]
ANTENNA_PATTERNS_CLASSES = [adp.Base(), adp.Base(), adp.Base(), adp.Base(), adp.File(PY_FILTERS)]
ANTENNA_PATTERNS_PROPNAMES = ["", "", "", "", "Select factory source file:"]
POLARIZATION= ["V", "H", "VH","cross", "custom"]
POLARIZATION_CLASSES  = [adp.Base(), adp.Base(), adp.Base(), adp.Base(), adp.Vec2(0,0)]
POLARIZATION_PROPNAMES = ["","","","", "Select slant angles:"]
POLARIZATION_MODEL = ["tr38901_1", "tr38902_2", "custom"]
POLARIZATION_MODEL_CLASSES = [adp.Base(),adp.Base(),adp.File(PY_FILTERS)]
POLARIZATION_MODEL_PROPNAMES = ["", "", "Select source file:"]


@dataclass_json
@dataclass
class ITUMaterials:
    ITU_name: adp.String

create_ITU = lambda : ITUMaterials(
    ITU_name=adp.String("concrete", True, ITU_MATERIALS, 0, name="ITU name"),
)

@dataclass_json
@dataclass
class CustomMaterials:
    thickness:adp.Real
    relative_permittivity:adp.Real
    conductivity: adp.Real
    scattering_coefficient: adp.Real
    xpd_coefficient:adp.Real
    scattering_pattern: adp.Toggle

create_custom = lambda : CustomMaterials(
    thickness=adp.Real(0.1, name="Thickness"),
    relative_permittivity=adp.Real(1.0, name= "Relative Permittivity"),
    conductivity=adp.Real(0.0, name="Conductivity"),
    scattering_coefficient = adp.Real(0.0, name="Scattering coefficient"),
    xpd_coefficient = adp.Real(0.0, name="XPD coefficient"),
    scattering_pattern=adp.Toggle(SCATTERING_PATTERNS_CLASSES, SCATTERING_PATTERNS, SCATTERING_PATTERNS_PROPNAMES, name="Scattering pattern")
)

MATERIAL_TYPES = [create_ITU, create_custom]
    
PRELOADED_SCENES = ["Blank", "Box", "Box one screen", "Box two screens", "Double reflector", "Etoile", "Floor wall", "Florence", "Munich", "Simple reflector", "Simple street canyon", "Simple street canyon with cars", "Simple wedge", "Triple reflector"]

@dataclass_json
@dataclass
class SetupSettings:

    #Scene base parameters
    frequency:adp.Real
    bandwidth:adp.Real
    temperature:adp.Real


create_SetupSettings = lambda : SetupSettings(
    frequency=adp.Real(3.5e9, name="Frequency"),
    bandwidth=adp.Real(1e6, name= "Bandwidth"),
    temperature=adp.Real(293, name="Temperature"),
)

@dataclass_json
@dataclass
class BackgroundScene:
    base_scene:adp.String

create_BackgroundScene = lambda : BackgroundScene(
    base_scene=adp.String("None", True, options = PRELOADED_SCENES, chosen=0, name="Base scene"),
)

@dataclass_json
@dataclass
class RenderSettings:
    #Render base parameters
    fov: adp.Real
    lighting_scale:adp.Real
    resolution: adp.Vec2 
    clip_at:adp.Real 
    clip_plane_orientation:adp.Vec3
    return_bitmap:adp.Boolean
    num_samples: adp.Integer
    envmap:adp.File
    camera:adp.Camera

create_RenderSettings = lambda : RenderSettings(
    fov= adp.Real(45.0, name="Field of view"),
    lighting_scale=adp.Real(1, name="Lighting scale") ,
    resolution= adp.Vec2(655,500, name="Resolution"),
    clip_at=adp.Real(-1,extra_case=-1, name="Clip at"), 
    clip_plane_orientation=adp.Vec3(0,0,-1, name="Clip plane orientation"),
    return_bitmap=adp.Boolean(False, name="Return bitmap"),
    num_samples= adp.Integer(512, name="Number of samples"),
    envmap=adp.File(IMAGE_FILTERS, name="Envmap"),
    camera=adp.Camera(name="Camera"),
)


@dataclass_json
@dataclass
class Camera:
    position:adp.Vec3
    localization:adp.Toggle

create_Camera = lambda:Camera(
    position = adp.Vec3(-250,250,150, name="Position"),
    localization = adp.Toggle([adp.Vec3(-15,30,28), adp.Vec3(0,0,0)], ["look_at","orientation"], name="Localization")
)

@dataclass_json
@dataclass
class Sample_Positions:

    activate:adp.Boolean
    num_positions:adp.Integer
    metric: adp.String
    min_val_db:adp.Real
    max_val_db:adp.Real
    min_dist: adp.Real
    max_dist: adp.Real
    tx_association: adp.Boolean
    center_pos: adp.Boolean
    seed: adp.Integer

create_Sample_Positions = lambda:Sample_Positions(
    activate = adp.Boolean(False),
    num_positions = adp.Integer(100, name="Number of positions"),
    metric = adp.String("path_gain", True, ["path_gain", "rss", "SINR"], 0, name="Sampling metric"),
    min_val_db = adp.Real(-100, name="Min. dB value"),
    max_val_db = adp.Real(200, name="Max. dB value"),
    min_dist = adp.Real(50, name="Min. distance"),
    max_dist = adp.Real(1000, name="Max. distance"),
    tx_association = adp.Boolean(True, name="Transmitter association"),
    center_pos = adp.Boolean(False, name="Center position"),
    seed =adp.Integer(1, name="Seed"),
)


@dataclass_json
@dataclass
class Resizing:

    activate:adp.Boolean
    center: adp.Vec3 
    orientation: adp.Vec3 
    size:adp.Vec2 

create_Resizing = lambda:Resizing(
    activate = adp.Boolean(False),
    center = adp.Vec3(0,0,0, name="Center"),
    orientation = adp.Vec3(0,0,0, name="Orientation"),
    size = adp.Vec2(400,400, name="Size"),
)

@dataclass_json
@dataclass
class Rescaling:
    activate: adp.Boolean
    rm_vmax: adp.Real
    rm_vmin: adp.Real


create_Rescaling = lambda:Rescaling(
    activate = adp.Boolean(False),
    rm_vmax= adp.Real(-1, name="Vmax"),
    rm_vmin=adp.Real(-1, name="Vmin"),
)

@dataclass_json
@dataclass
class Transmitter:

    position: adp.Vec3 
    power_dbm: adp.Real
    localization:adp.Toggle
    velocity: adp.Vec3

create_Transmitter = lambda : Transmitter(
    position = adp.Vec3(0,0,0,"defaultname", name="Position"),
    power_dbm=adp.Real(44, name="Power dBm"),
    localization = adp.Toggle([adp.Vec3(0,0,0), adp.Vec3(0,0,0)], ["orientation","look_at"], name="Localization"),
    velocity= adp.Vec3(0,0,0,"defaultname", name="Velocity"),
)

@dataclass_json
@dataclass
class Receiver:

    position: adp.Vec3
    localization:adp.Toggle
    velocity: adp.Vec3

create_Receiver = lambda : Receiver(
    position = adp.Vec3(0,0,0,"defaultname", name="Position"),
    localization = adp.Toggle([adp.Vec3(0,0,0), adp.Vec3(0,0,0)], ["orientation","look_at"], name="Localization"),
    velocity= adp.Vec3(0,0,0,"defaultname", name="Velocity"),
    #color=adp.Vec3(0,0,0,"defaultname"),
    #display_radius=adp.Real(0),
)

@dataclass_json
@dataclass
class Path:
    max_depth:adp.Integer
    max_number_paths_per_src: adp.Integer 
    samples:adp.Integer 
    synthetic_array: adp.Boolean 
    los: adp.Boolean
    specular_reflection:adp.Boolean 
    diffuse_reflection:adp.Boolean
    refraction: adp.Boolean
    seed:adp.Integer
    num_subcarriers:adp.Integer
    subcarrier_spacing:adp.Real
    low_pass_bandwidth:adp.Real
    l_min:adp.Real
    l_max:adp.Real
    normalize_energy:adp.Boolean
    normalize_delays:adp.Boolean
    sampling_frequency:adp.Toggle

create_Path = lambda : Path(
    max_depth = adp.Integer(10,name="Max depth"),
    max_number_paths_per_src = adp.Integer(1000000, name="Max # paths per source"),
    samples = adp.Integer(1000000, name="Samples"),
    synthetic_array = adp.Boolean(True, name="Synthetic array"),
    los = adp.Boolean(False, name="Line of Sight"),
    specular_reflection=adp.Boolean(False, "Specular reflection"),
    diffuse_reflection = adp.Boolean(False, "Diffuse reflection"),
    seed = adp.Integer(10, name="Seed"),
    refraction = adp.Boolean(False, name="Refraction"),
    num_subcarriers = adp.Integer(1024, name="Number of subcarriers"),
    subcarrier_spacing = adp.Real(30e3, name="Subcarrier spacing"),
    low_pass_bandwidth = adp.Real(100e6, min=0, name="Low pass bandwidth"),
    l_min = adp.Real(0, name="Minimum time lag"),
    l_max = adp.Real(100, name="Maximum time lag"),
    normalize_energy = adp.Boolean(True, name= "Normalize energy"),
    normalize_delays = adp.Boolean(True, name = "Normalize delays"),
    sampling_frequency=adp.Toggle([adp.Base(), adp.Real(1/100e6)], ["Nyquist", "Custom"], name="Sampling frequency")
)



@dataclass_json
@dataclass
class RadioMap:
    samples:adp.Integer 
    los: adp.Boolean
    specular_reflection:adp.Boolean 
    diffuse_reflection:adp.Boolean
    refraction: adp.Boolean
    max_depth:adp.Integer
    seed:adp.Integer
    stop_threshold:adp.Integer 
    cell_size:adp.Vec2
    rr_depth: adp.Integer 
    rr_prob: adp.Real 
    rm_db_scale: adp.Boolean
    rm_metric: adp.String
    rm_show_color_bar:adp.Boolean
    resizing: adp.Resizing
    rescaling: adp.Rescaling
    sample_positions:adp.Sample_Positions
    

create_RadioMap = lambda : RadioMap(
    samples = adp.Integer(1000000, name="Samples"),
    los = adp.Boolean(True, name="Line of Sight"),
    specular_reflection=adp.Boolean(True, name="Specular reflection"),
    diffuse_reflection = adp.Boolean(False, name="Diffuse reflection"),
    max_depth = adp.Integer(3, name="Max depth"), 
    seed = adp.Integer(42, name="Seed"),
    stop_threshold = adp.Integer(-20000, name="Stop threshold"),
    refraction = adp.Boolean(True, name="Refraction"),
    cell_size = adp.Vec2(5,5, name="Cell size"),
    rr_depth = adp.Integer(-1, name="Russian roulette depth"),
    rr_prob = adp.Real(0.95, name="Russian roulette probability"),
    rm_db_scale= adp.Boolean(True, name="dB scale"),
    rm_metric=adp.String("path_gain", True, ["path_gain", "rss", "sinr"],0, name="Metric to show"),
    rm_show_color_bar=adp.Boolean(False, name="Show colorbar"),
    resizing=adp.Resizing(name="Resizing"),
    rescaling=adp.Rescaling(name="Rescaling"),
    sample_positions=adp.Sample_Positions(name="Sample positions"),
    
)

SOLVERS = [create_RadioMap, create_Path]

@dataclass_json
@dataclass
class Antenna:
    tx_array:adp.AntennaArray
    rx_array:adp.AntennaArray

create_Antenna = lambda : Antenna(
    tx_array = adp.AntennaArray(name="Transmitter array"),
    rx_array = adp.AntennaArray(name="Receiver array"),
)

@dataclass_json
@dataclass
class AntennaArray:
    num_rows:adp.Integer
    num_cols:adp.Integer
    vertical_spacing:adp.Real
    horizontal_spacing:adp.Real
    pattern:adp.Toggle
    polarization:adp.Toggle
    polarization_model:adp.Toggle

create_AntennaArray = lambda : AntennaArray(
    num_rows=adp.Integer(1, name="Number of rows"),
    num_cols = adp.Integer(1, name="Number of columns"),
    vertical_spacing=adp.Real(0.5, min=0, name="Vertical spacing"),
    horizontal_spacing=adp.Real(0.5, min=0,  name="Horizontal spacing"),
    pattern = adp.Toggle(ANTENNA_PATTERNS_CLASSES, ANTENNA_PATTERNS, ANTENNA_PATTERNS_PROPNAMES, name="Pattern"),
    polarization=adp.Toggle(POLARIZATION_CLASSES, POLARIZATION, POLARIZATION_PROPNAMES, name="Polarization"),
    polarization_model=adp.Toggle(POLARIZATION_MODEL_CLASSES, POLARIZATION_MODEL, POLARIZATION_MODEL_PROPNAMES, name="Polarization model"),
)


@dataclass_json
@dataclass
class SimulationOutput(ApiSimulationBase):
    """
    Complete simulation configuration.
    
    This class combines all the individual settings components into a single
    structure that fully defines a simulation. This is the main data structure
    passed from the UI to the solver code.
    """
    scene:CatchAll


@dataclass_json
@dataclass
class Simulations(BaseSimulations):
    """
    Container for multiple simulation configurations.
    
    This class is used when multiple simulations need to be defined and
    executed as a batch.
    """
    simulations: list[SimulationOutput]  # List of individual simulation configurations
