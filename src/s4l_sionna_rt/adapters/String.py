import XCore as xc

class String:
    def __init__(self, initial_value,  dropdown=False, options=[], chosen=0, name=None):
        self.value = initial_value
        self.dropdown = dropdown
        self.options = options 
        self.chosen = chosen
        self.name=name

    def draw(self, parent, name):
        if not self.dropdown:
            new_prop = xc.PropertyString(self.value) # value, min, max
        else:
            new_prop = xc.PropertyEnum(
                self.options,self.chosen
            )
            self.value = new_prop.ValueDescription
            
        # new_prop.OnModified.Connect(lambda property, mod_type : self._update(property, mod_type))
        if self.name != None:
            new_prop.Description = self.name
        new_prop.OnModified.Connect(self._update)
        parent.Add(name, new_prop)

    def validate(self):
        return True, ""

    def _update(self, property, mod_type: xc.PropertyModificationTypeEnum):
        if mod_type != xc.kPropertyModified:
                return
        if self.dropdown:
            self.value = property.ValueDescription
            self.chosen = property.Value
        else:
            self.value = property.Value

    def to_format(self, prop_name, results_dir):
        return {prop_name:self.value}
    
