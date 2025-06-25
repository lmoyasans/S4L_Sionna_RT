from setuptools import find_packages, setup

setup(
    name="s4l-sionna-rt-plugin",
    version="1.0.0",
    description="A simulation plugin for Ray-Tracing electromagnetics in S4L",
    author="Lucia Moya-Sans",
    author_email="moyasans@itis.swiss",
    package_dir={"": "src"},  # This tells setuptools to look in the src directory
    packages=find_packages(where="src"),  # This finds packages inside src
    python_requires=">=3.8",
    install_requires=[
        "sionna",
        "scipy >= 1.14.1",
        "matplotlib >= 3.10",
        "sionna-rt >= 1.0.2",
        "tensorflow >= 2.14, !=2.16, !=2.17",
        "numpy >= 1.26, <2.0",
        "importlib_resources >= 6.4.5"
    ],
    entry_points={
        "s4l.simulator_plugins": [
            "s4l_sionna_rt = s4l_sionna_rt.register:register",
        ],
    },
)
