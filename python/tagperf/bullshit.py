def helvetify():
    """
    Load 'Helvetica' default font (may be Arial for now)
    """
    from matplotlib import rc
    # 'Comic Sans MS', 'Trebuchet MS' works, Arial works in png...
    rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
