# Sim4Life Sionna RT Simulator Plugin

## Description

This plugin for [Sim4Life](https://sim4life.swiss/) integrates the [Sionna RT](https://github.com/NVlabs/sionna-rt) differentiable ray tracing library, enabling advanced simulation capabilities for modeling radio wave propagation in complex environments.

Leveraging [Sim4Life](https://sim4life.swiss/) capabilities, the plugin offers interactive 3D modelling tools and an intuitive graphical user interface (GUI), supporting direct modelling, editing and rendering of scenes. Users can visualize propagation paths, radio maps, and coverage with just a few clicks. This makes creating and managing complex radio propagation scenarios effortless. 

## Mathematical Model

It makes use of [Sionna RT](https://github.com/NVlabs/sionna-rt) to simulate electromagnetic radio wave propagation using algorithms based on shooting and bouncing rays (SBR) and the image method. 

[Sionna RT](https://github.com/NVlabs/sionna-rt) supports differentiable computation, enabling gradients of CIRs and radio maps with respect to system and environmental parameters such as material properties, antenna patterns, and object positions

For more information about the underlying concepts, please visit [Sionna RT Technical Report](https://nvlabs.github.io/sionna/rt/tech-report/)

## Features

- Support for custom 3D scenes and material properties

- Integration with the [Sim4Life](https://sim4life.swiss/) modeling environment

- Generation of:

  - Channel impulse responses (CIRs)
  
  - Channel frequency responses (CFRs)

  - Radio maps (coverage/power maps)

- Visualization of propagation paths and radio maps

## Usage

1. Create a new simulation by selecting "Sionna RT" from the simulation types

2. Import or define the 3D scene and material properties (you may use the base scenes, imported files in the supported formats or your own 3D objects modeled in Sim4Life)

3. Specify transmitter and receiver locations, antenna patterns, and system parameters (Receiver locations are optional for radio map solvers)

4. Configure simulation options (e.g., maximum number of bounces, frequency, resolution)

5. Run the simulation to compute CIRs or radio maps

6. Visualize propagation paths, radio maps, and analyze results


## Technical implementation

This plugin is implemented with:
- Model classes for simulation, scene, object settings and output retrieval
- Adapter classes that generalize property creation, UI drawing and serialization
- Controller classes for UI and workflow integration
- Loaders for factories in [Sionna RT](https://github.com/NVlabs/sionna-rt) format for custom scattering, polarization and antenna patterns
- Ray tracing solver backend powered by [Sionna RT](https://github.com/NVlabs/sionna-rt)

## Installation

The plugin can be installed directly to [Sim4Life](https://sim4life.swiss/) using the community store plugin installer.

For development installations:

```bash
git clone <repository-url>
cd S4L_Sionna_RT
pip install -e .
```

## Usage

This plugin will be automatically detected by [Sim4Life](https://sim4life.swiss/) when installed via pip in the internal environment (development purposes) or by the community store.


## Citation

If you are using this code in academic research, we would be grateful if you could cite Sim4Life, our library and the original Sionna repository:

```bibtex
@misc{sim4life,
  title = {Sim4Life},
  author = {{ZMT Zurich MedTech AG} and {IT'IS Foundation}},
  note = {https://sim4life.swiss/}
}

@software{s4l-sionna,
 title = {S4l Sionna RT Plugin},
 author = {Moya-Sans, Lucia},
 note = {https://github.com/lmoyasans/S4L_Sionna_RT},
 year = {2025},
 version = {1.0.0}
}

@software{sionna,
 title = {Sionna},
 author = {Hoydis, Jakob and Cammerer, Sebastian and {Ait Aoudia}, Fayçal and Nimier-David, Merlin and Maggi, Lorenzo and Marcus, Guillermo and Vem, Avinash and Keller, Alexander},
 note = {https://nvlabs.github.io/sionna/},
 year = {2022},
 version = {1.0.2}
}
```