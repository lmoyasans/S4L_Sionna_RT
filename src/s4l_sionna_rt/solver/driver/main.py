# # # # Sionna RT simulation 
# # # # -----------------------------------------

import argparse
import json
import logging
import os
import sys
import inspect
import importlib.util
import numpy as np
import pyvista as pv
from s4l_sionna_rt.solver.driver.api_models import SimulationOutput
from s4l_sionna_rt.solver.driver.SionnaLoader import SionnaLoader
import sionna.rt as rt
import mitsuba as mi

def custom_json(obj):
    if isinstance(obj,complex):
        return {'__complex__':True, 'real':obj.real, 'imag':obj.imag}



# # --- CLI Argument Parsing ---
parser = argparse.ArgumentParser(description="Sionna RT Solver")
parser.add_argument(
    "-i",
    "--inputfile",
    type=str,
    required=True,
    help="Path to simulation input JSON file containing model parameters"
)
parser.add_argument(
    "-o", 
    "--outputfolder", 
    type=str, 
    required=True, 
    help="Path to output folder for solver results and visualization files"
)
args = parser.parse_args()

# # --- Setup Logging ---
# # Configure both console and file logging to track solver execution
# input_path = os.path.abspath(args.inputfile)
output_dir = os.path.abspath(args.outputfolder)
os.makedirs(output_dir, exist_ok=True)
log_path = os.path.join(output_dir, "solver.log")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# # --- Load and Parse Input JSON ---
# Load the simulation configuration created through the S4L UI
with open(args.inputfile, "r") as f:
    scene_params = SimulationOutput.from_json(f.read()).scene # pyright: ignore[reportGeneralTypeIssues]


SCENES = {
    "Box" : rt.scene.box, 
    "Box one screen":rt.scene.box_one_screen, 
    "Box two screens":rt.scene.box_two_screens, 
    "Double reflector": rt.scene.double_reflector, 
    "Etoile": rt.scene.etoile, 
    "Floor wall":rt.scene.floor_wall, 
    "Florence":rt.scene.florence, 
    "Munich":rt.scene.munich, 
    "Simple reflector":rt.scene.simple_reflector, 
    "Simple street canyon":rt.scene.simple_street_canyon, 
    "Simple street canyon with cars":rt.scene.simple_street_canyon_with_cars, 
    "Simple wedge":rt.scene.simple_wedge, 
    "Triple reflector":rt.scene.triple_reflector,
}


solver_settings = scene_params["Solver_Settings"]
setup_settings = scene_params["Setup_settings"]
antennas = scene_params["Antennas"]
materials = scene_params["Materials"]
render_settings = scene_params["Render_Settings"]

## Setup for custom antenna or scattering patterns, polarization models and polarizations

customLoader = SionnaLoader()


##############################################
###              Create scene              ###
##############################################

print(scene_params["base_scene"])

if scene_params["base_scene"] in SCENES.keys():
    scene = rt.load_scene(SCENES[scene_params["base_scene"]])
else:
    scene = rt.load_scene()
scene.frequency = setup_settings["frequency"]
scene.bandwidth = setup_settings["bandwidth"]
scene.temperature = setup_settings["temperature"]


##############################################
###          Create antenna setup          ###
##############################################

if isinstance(antennas["tx_array"]["pattern"], dict):
    t_pattern = customLoader.register_antenna_patterns(antennas["tx_array"]["pattern"]["custom"])[0]
else:
    t_pattern = antennas["tx_array"]["pattern"]

if isinstance(antennas["tx_array"]["polarization"], dict):
    t_polarization = customLoader.register_polarizations(antennas["tx_array"]["polarization"]["custom"])
else:
    t_polarization = antennas["tx_array"]["polarization"]

if isinstance(antennas["tx_array"]["polarization_model"],dict):
    t_polarization_model = customLoader.register_polarization_models(antennas["tx_array"]["polarization_model"]["custom"])
else:
    t_polarization_model = antennas["tx_array"]["polarization_model"]
logger.debug(antennas["tx_array"]["vertical_spacing"])
scene.tx_array = rt.PlanarArray(num_rows=antennas["tx_array"]["num_rows"], 
                                num_cols = antennas["tx_array"]["num_cols"], 
                                vertical_spacing = antennas["tx_array"]["vertical_spacing"],
                                horizontal_spacing = antennas["tx_array"]["horizontal_spacing"],
                                pattern = t_pattern,
                                polarization = t_polarization,
                                polarization_model = t_polarization_model,
                )

if isinstance(antennas["rx_array"]["pattern"], dict):
    r_pattern = customLoader.register_antenna_patterns(antennas["rx_array"]["pattern"]["custom"])[0]
else:
    r_pattern = antennas["rx_array"]["pattern"]

if isinstance(antennas["rx_array"]["polarization"], dict):
    r_polarization = customLoader.register_polarizations(antennas["rx_array"]["polarization"]["custom"])
else:
    r_polarization = antennas["rx_array"]["polarization"]

if isinstance(antennas["rx_array"]["polarization_model"],dict):
    r_polarization_model = customLoader.register_polarization_models(antennas["rx_array"]["polarization_model"]["custom"])
else:
    r_polarization_model = antennas["rx_array"]["polarization_model"]
scene.rx_array = rt.PlanarArray(num_rows=antennas["rx_array"]["num_rows"], 
                                num_cols = antennas["rx_array"]["num_cols"], 
                                vertical_spacing = antennas["rx_array"]["vertical_spacing"],
                                horizontal_spacing = antennas["rx_array"]["horizontal_spacing"],
                                pattern = r_pattern,
                                polarization = r_polarization,
                                polarization_model = r_polarization_model,
                )

trx=[]
for i,tr in enumerate(antennas["transmitters"].keys()):
    if antennas["transmitters"][tr]["velocity"] == [0,0,0]:
        velocity = None
    else:
        velocity = antennas["transmitters"][tr]["velocity"]
    if "look_at" in antennas["transmitters"][tr]["localization"].keys():
        trx.append(rt.Transmitter(tr, 
                                    look_at = antennas["transmitters"][tr]["localization"]["look_at"], 
                                    position = antennas["transmitters"][tr]["position"],
                                    velocity = velocity, 
                                    power_dbm = antennas["transmitters"][tr]["power_dbm"],
                    )
                )
    else:
        trx.append(rt.Transmitter(tr, 
                                    orientation = antennas["transmitters"][tr]["localization"]["orientation"], 
                                    position = antennas["transmitters"][tr]["position"],
                                    velocity = velocity, 
                                    power_dbm = antennas["transmitters"][tr]["power_dbm"],
                    )
                )
    scene.add(trx[i])


rx=[]
if len(antennas["receivers"].keys())!=0:
    for i,r in enumerate(antennas["receivers"].keys()):
        if antennas["receivers"][r]["velocity"] == [0,0,0]:
            velocity = None
        else:
            velocity = antennas["receivers"][r]["velocity"]
        if "look_at" in antennas["receivers"][r]["localization"].keys():
            rx.append(rt.Receiver(r, 
                                        look_at = antennas["receivers"][r]["localization"]["look_at"], 
                                        position = antennas["receivers"][r]["position"],
                                        velocity = velocity, 
                        )
                    )
        else:
            rx.append(rt.Receiver(r, 
                                        orientation = antennas["receivers"][r]["localization"]["orientation"], 
                                        position = antennas["receivers"][r]["position"],
                                        velocity = velocity, 
                        )
                    )
        scene.add(rx[i])

##############################################
###   Create materials and object setup    ###
##############################################

if len(materials)!=0:
    mats=[]
    objs = []
    for i,mat in enumerate(materials.keys()):
        if materials[mat]["type"]=="ITUMaterials":
            print(materials[mat]["ITU_name"])
            mats.append(rt.ITURadioMaterial(name = mat, itu_type=materials[mat]["ITU_name"], thickness=0.1,  color=(0.8, 0.1, 0.1)))
            for j,obj in enumerate(materials[mat]["geometries"]):
                logger.debug(obj["fname"])
                logger.debug(obj["name"])
                objs.append(
                    rt.SceneObject(fname = obj["fname"], name = obj["name"], radio_material = mats[i])
                )
        else:
            if isinstance(materials[mat]["scattering_pattern"],dict):
                scat_p = customLoader.register_scattering_patterns(materials[mat]["scattering_pattern"]["custom"])[0]
            else:
                scat_p = materials[mat]["scattering_pattern"]
            mats.append(rt.RadioMaterial(name=mat, thickness = materials[mat]["thickness"], 
                                         relative_permittivity = materials[mat]["relative_permittivity"],
                                         conductivity = materials[mat]["conductivity"],
                                         scattering_coefficient = materials[mat]["scattering_coefficient"],
                                         xpd_coefficient = materials[mat]["xpd_coefficient"],
                                         scattering_pattern=scat_p))
            for j,obj in enumerate(materials[mat]["geometries"]):
                print(obj["fname"])
                objs.append(
                    rt.SceneObject(fname = "input_files/dee5f659-4795-48b3-a0fa-fe9551866908.ply", name = obj["name"], radio_material = mats[i])
                )
    logger.debug(objs[0].position)
    logger.debug(objs[0].orientation)
    scene.edit(add=objs)

##############################################
###          Create solver setup           ###
##############################################

if "look_at" in render_settings["camera"]["localization"].keys():
    my_cam = rt.Camera(position=render_settings["camera"]["position"], look_at=render_settings["camera"]["localization"]["look_at"])
else:
    my_cam = rt.Camera(position=render_settings["camera"]["position"], orientation=render_settings["camera"]["localization"]["orientation"]) 


if solver_settings["type"] == "RadioMap":

    solver = rt.RadioMapSolver()
    rm = solver(scene=scene, 
                center = mi.Point3f(solver_settings["center"]),
                orientation = mi.Point3f(solver_settings["orientation"]),
                size=mi.Point2f(solver_settings["size"]),
                cell_size=mi.Point2f(solver_settings["cell_size"]),
                samples_per_tx=solver_settings["samples"],
                max_depth=solver_settings["max_depth"],
                los=solver_settings["los"],
                specular_reflection=solver_settings["specular_reflection"],
                diffuse_reflection = solver_settings["diffuse_reflection"],
                refraction = solver_settings["refraction"],
                seed = solver_settings["seed"],
                rr_depth=solver_settings["rr_depth"],
                rr_prob = solver_settings["rr_prob"],
                stop_threshold=solver_settings["stop_threshold"]
                )

    summary = {
        "type":"RadioMap",
        "path_gain":rm.path_gain.numpy().tolist(),
        "rss": rm.rss.numpy().tolist(),
        "sinr": rm.sinr.numpy().tolist(),
        "image":output_dir + "/render_file.png",
    }

    if solver_settings["sample_positions"]["activate"] == True:
        positions,cell_ids = rm.sample_positions(num_pos=solver_settings["sample_positions"]["num_positions"], 
                                          metric = solver_settings["sample_positions"]["metric"],
                                          min_val_db = solver_settings["sample_positions"]["min_val_db"],
                                          max_val_db = solver_settings["sample_positions"]["max_val_db"],
                                          min_dist = solver_settings["sample_positions"]["min_dist"],
                                          max_dist = solver_settings["sample_positions"]["max_dist"],
                                          tx_association = solver_settings["sample_positions"]["tx_association"],
                                          center_pos = solver_settings["sample_positions"]["center_pos"],
                                          seed = solver_settings["sample_positions"]["seed"]
        )

        positions = np.squeeze(positions.numpy())

        summary.update({"positions": positions.tolist(), "cell_ids":cell_ids.numpy().tolist()})
        for l,tx in enumerate(positions):
            for ll, p in enumerate(tx):
                r = rt.Receiver(f"rx-{len(positions[1])*l + ll}", position = p.tolist(), orientation = [0,0,0])
                scene.add(r)
                rx.append(r)

    scene.render_to_file(camera=my_cam, filename = output_dir + "/render_file.png", radio_map = rm, 
                        fov = render_settings["fov"],
                        lighting_scale=render_settings["lighting_scale"],
                        clip_plane_orientation=render_settings["clip_plane_orientation"],
                        envmap=render_settings["envmap"],
                        num_samples = render_settings["num_samples"],
                        resolution=(int(render_settings["resolution"][0]),int(render_settings["resolution"][1])),
                        rm_db_scale= solver_settings["rm_db_scale"], 
                        rm_vmin = solver_settings["rm_vmin"], 
                        rm_vmax = solver_settings["rm_vmax"], 
                        rm_metric=solver_settings["rm_metric"],
                        )
        

    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2,  default=custom_json)
else:
    solver = rt.PathSolver()
    paths = solver(scene=scene, 
                max_depth = solver_settings["max_depth"], 
                max_num_paths_per_src=solver_settings["max_number_paths_per_src"],
                samples_per_src=solver_settings["samples"],
                synthetic_array=solver_settings["synthetic_array"],
                los=solver_settings["los"],
                specular_reflection=solver_settings["specular_reflection"],
                diffuse_reflection=solver_settings["diffuse_reflection"],
                refraction=solver_settings["refraction"],
                seed = solver_settings["seed"]
                )
    
    print(paths)

    scene.render_to_file(camera=my_cam, 
                        filename = output_dir + "/render_file.png" ,
                        fov = render_settings["fov"],
                        lighting_scale=render_settings["lighting_scale"],
                        clip_plane_orientation=render_settings["clip_plane_orientation"],
                        envmap=render_settings["envmap"],
                        num_samples = render_settings["num_samples"],
                        resolution=render_settings["resolution"],
                        paths=paths
                        )


    a, tau = paths.cir(normalize_delays=True, out_type="numpy")
    # Shape: [num_rx, num_rx_ant, num_tx, num_tx_ant, num_paths, num_time_steps]
    print("Shape of a: ", a.shape)

    # Shape: [num_rx, num_rx_ant, num_tx, num_tx_ant, num_paths]
    tau = tau/1e-9  #Scaled to ns
    print("Shape of tau: ", tau.shape)

    # Compute frequencies of subcarriers relative to the carrier frequency
    frequencies = rt.subcarrier_frequencies(solver_settings["num_subcarriers"], solver_settings["subcarrier_spacing"])

    # Compute channel frequency response
    h_freq = paths.cfr(frequencies=frequencies,
                    normalize=solver_settings["normalize_energy"],  # Normalize energy
                    normalize_delays=solver_settings["normalize_delays"],
                    out_type="numpy")

    # Shape: [num_rx, num_rx_ant, num_tx, num_tx_ant, num_time_steps, num_subcarriers]
    print("Shape of h_freq: ", h_freq.shape)

    if isinstance(solver_settings["sampling_frequency"],dict):
        sampling_frequency = solver_settings["sampling_frequency"]["Custom"]
    else:
        sampling_frequency = None

    taps = paths.taps(bandwidth=solver_settings["low_pass_bandwidth"], # Bandwidth to which the channel is low-pass filtered 
                  l_min=solver_settings["l_min"],        # Smallest time lag
                  l_max=solver_settings["l_max"],       # Largest time lag
                  sampling_frequency=sampling_frequency, # Sampling at Nyquist rate, i.e., 1/bandwidth
                  normalize=solver_settings["normalize_energy"],  # Normalize energy
                  normalize_delays=solver_settings["normalize_delays"],
                  out_type="numpy")
    print("Shape of taps: ", taps.shape)

    summary = {
        "type":"Path",
        "a":a.tolist(),
        "tau": tau.tolist(),
        "h_freq": h_freq.tolist(),
        "taps": taps.tolist(),
        "image":output_dir + "/render_file.png",
    }

    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=custom_json)