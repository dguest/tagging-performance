
def get_taggers(in_file): 
    return in_file['B/btag/all/'].keys()

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
