import XCore as xc
import logging
import shutil
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class File:
    def __init__(self, filter, allow_none = True, name=None): 
        self.value = None
        self.filter = filter
        self.allow_none = allow_none
        self.name = name

    def draw(self, parent, name):
        new_prop = xc.PropertyFile(is_folder=False, is_input=True)
        new_prop.Filter = self.filter
        new_prop.OnModified.Connect(self._update)
        if self.name != None:
            new_prop.Description = self.name
        parent.Add(name, new_prop)

    def _update(self, property: xc.PropertyReal, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
                return
        self.value = property.Value

    def validate(self):
        if not self.allow_none and self.value == None:
            return False, "File selection required"
        elif not self.allow_none and os.path.exists(self.value):
            return False, "File selection required"
        return True, ""

    def to_format(self, prop_name, results_dir):
        if self.value!=None and os.path.exists(self.value):
            filename = Path(self.value).name
            dst = results_dir / "input_files" / filename
            shutil.copyfile(self.value, dst)
            return {prop_name:str("input_files/" + filename)}
        else:
            return {prop_name:None}
    
