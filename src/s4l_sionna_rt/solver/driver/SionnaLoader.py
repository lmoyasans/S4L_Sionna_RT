import importlib.util
import inspect
import logging
from typing import Optional, Dict
from sionna.rt import (
    PolarizedAntennaPattern,
    ScatteringPattern,
    register_antenna_pattern,
    register_scattering_pattern,
    register_polarization,
    register_polarization_model,
)

logger = logging.getLogger(__name__)

class SionnaLoader:
    """
    Dynamically loads and registers antenna pattern factories and
    scattering pattern classes from a user Python file.
    """

    def __init__(self, objs:Optional[Dict[str, float]] = None, module_path: Optional[str] = None):
        self.module_path = module_path
        if module_path!=None:
            if objs!=None:
                self.registrations = self.register_all(module_path, objs)
            else:
                self.registrations = self.register_all(module_path)

    def _load_module(self, module_path):
        spec = importlib.util.spec_from_file_location("user_patterns", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def register_antenna_patterns(self, module_path, prefix="custom_"):
        module = self._load_module(module_path)
        factories = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                # Heuristic: must accept 'polarization' and 'polarization_model'
                if (
                    "polarization" in sig.parameters
                    and "polarization_model" in sig.parameters
                    and sig.return_annotation == PolarizedAntennaPattern
                ):
                    # Optionally check return type annotation
                    factories.append((name, obj))
                    register_antenna_pattern(f"{prefix}{name}", obj)
                    logger.debug(f"Registered antenna pattern: {prefix}{name}")
        return [f"{prefix}{name}" for name, _ in factories]

    def register_polarizations(self,  objs, prefix="custom_"):
        registered = []
        for name in objs.keys():
            obj = objs[name]
            # Look for lists of one or two floats (slant angles)
            if (
                isinstance(obj, list)
                and len(obj) in [1, 2]
                and all(isinstance(x, float) for x in obj)
            ):
                reg_name = f"{prefix}{name}"
                register_polarization(reg_name, obj)
                registered.append(reg_name)
                logger.debug(f"Registered polarization: {reg_name}")
        return registered

    def register_polarization_models(self, module_path, prefix="custom_"):
        module = self._load_module(module_path)
        registered = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                if len(sig.parameters) != 4:
                    reg_name = f"{prefix}{name}"
                    register_polarization_model(reg_name, obj)
                    registered.append(reg_name)
                    print(f"Registered polarization model: {reg_name}")
        return registered

    def register_scattering_patterns(self, module_path, prefix="custom_"):
        module = self._load_module(module_path)
        classes = []
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, ScatteringPattern)
                and obj is not ScatteringPattern
            ):
                # Optionally check for __call__ method
                if hasattr(obj, "__call__"):
                    classes.append((name, obj))
                    register_scattering_pattern(f"{prefix}{name}", obj)
                    logger.debug(f"Registered scattering pattern: {prefix}{name}")
        return [f"{prefix}{name}" for name, _ in classes]


    def register_all(self, module_path, objs: Optional[Dict[str,float]] = None, prefix="custom_"):
        antenna_patterns = self.register_antenna_patterns(module_path, prefix)
        scattering_patterns = self.register_scattering_patterns(module_path, prefix)
        polarization_models = self.register_polarization_models(module_path, prefix)
        if objs!=None:
            polarizations = self.register_polarizations(objs, prefix)
            return {
                "antenna_patterns": antenna_patterns,
                "scattering_patterns": scattering_patterns,
                "polarization_models":polarization_models,
                "polarizations":polarizations,
            }
        else:
            return {
                "antenna_patterns": antenna_patterns,
                "scattering_patterns": scattering_patterns,
                "polarization_models":polarization_models,
            }
