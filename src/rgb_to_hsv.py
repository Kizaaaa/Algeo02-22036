import numpy as np

def rgb_to_hsv(r, g, b):
    r = r / 255.0
    g = g / 255.0
    b= b / 255.0

    Cmax = max(r, g, b)
    Cmin = min(r, g, b)

    v = Cmax

    if (Cmax != 0):
        s = (Cmax - Cmin) / Cmax
    else:
        s = 0
    
    if (s == 0):
        h = 0
    else:
        delta = Cmax - Cmin
        if (Cmax == r):
            h = 60 * (((g - b) / delta) % 6)
        elif (Cmax == g):
            h = 60 * (((b - r) / delta) + 2)
        else: # Cmax == b
            h = 60 * (((r - g) / delta) + 4)
    return h, s, v