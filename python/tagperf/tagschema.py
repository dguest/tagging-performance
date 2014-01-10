try: 
    import yaml
except ImportError: 
    import json as yaml
    def dump_proxy(obj, **args): 
        """
        monkey patch json to look like yaml
        """
        return yaml.dumps(obj)
    yaml.dump = dump_proxy

from os.path import isfile

class ColorScheme(dict): 
    """
    Keeps track of / assigns colors for the taggers. 
    Assignments are stored in a yaml file. 
    """
    colors = list('bgrcmyk') + ['orange', 'brown']
    def __init__(self, file_name): 
        self.yaml_file = file_name
        if isfile(file_name): 
            with open(file_name, 'r') as ymlfile: 
                self.update(yaml.load(ymlfile))
    def __enter__(self): 
        return self
    def __exit__(self, ex_type, ex_mess, tb): 
        self.write(self.yaml_file)
    def __getitem__(self, key): 
        if not key in self: 
            opts = set(self.colors) - set(self.values())
            if not opts: 
                raise KeyError("ran out of color keys")
            val = next(iter(opts))
            super().__setitem__(key, val)
            return val
        return super().__getitem__(key)
    def write(self, fname): 
        with open(fname,'w') as ymlfile: 
            out_str = yaml.dump(dict(self.items()), default_flow_style=False)
            ymlfile.write(out_str)
            

def get_taggers(in_file, subset=None): 
    taggers = set(in_file['B/btag/all/'].keys())
    if subset: 
        sset = set(subset)
        not_found = sset - taggers
        if not_found: 
            raise ValueError(
                "taggers don't exist: {}".format(', '.join(not_found)))
        taggers &= sset
    return sorted(taggers)

def get_pt_bins(group): 
    pt_bins = {}
    for binstr in group: 
        lowstr, highstr = binstr.split('-')
        low = float(lowstr)
        if low == 0.0: 
            continue
        high = float(highstr)
        if high == float('inf'): 
            continue
        pt_bins[binstr] = (low, high)
    return pt_bins
