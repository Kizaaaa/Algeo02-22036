import numpy as np

def bgr_to_hsv(b, g, r):
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

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

def hsv_to_bgr(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if (0 <= h < 60):
        r = c
        g = x
        b = 0
    elif (60 <= h < 120):
        r = x
        g = c
        b = 0
    elif (120 <= h < 180):
        r = 0
        g = c
        b = x
    elif (180 <= h < 240):
        r = 0
        g = x
        b = c
    elif (240 <= h < 300):
        r = x
        g = 0
        b = c
    else: # (300 <= h < 360)
        r = c
        g = 0
        b = x
    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255
    return b, g, r