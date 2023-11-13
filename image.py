from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def rgb_to_hsv(rgb_tuple):
    r, g, b = rgb_tuple
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
    h = (h + 360) % 360
    return int(h), int(s * 100), int(v * 100)

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
    r = round((r + m) * 255)
    g = round((g + m) * 255)
    b = round((b + m) * 255)
    return b, g, r

def image_to_hsv_matrix(image_path):
    image = Image.open(image_path)
    rgb_matrix = np.array(image)
    hsv_matrix = np.array([[rgb_to_hsv(pixel) for pixel in row] for row in rgb_matrix])
    return hsv_matrix

def hsv_average(hsv_matrix):
    rows, cols, _ = hsv_matrix.shape
    part_rows = rows // 4
    part_cols = cols // 4
    hsv_average = []
    for i in range(4):
        for j in range(4):
            part = hsv_matrix[i * part_rows : (i + 1) * part_rows, j * part_cols : (j + 1) * part_cols]
            average_h = round(np.mean(part[:, :, 0]), 2)
            average_s = round(np.mean(part[:, :, 1]), 2)
            average_v = round(np.mean(part[:, :, 2]), 2)
            hsv_average.append((average_h, average_s, average_v))
    return hsv_average

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = sum(a**2 for a in vector_a) ** 0.5
    norm_b = sum(b**2 for b in vector_b) ** 0.5
    if norm_a == 0 and norm_b == 0:
        return 1.0
    elif norm_a == 0 or norm_b == 0:
        return 0.0
    cosine_similarity_value = dot_product / (norm_a * norm_b)
    return cosine_similarity_value

def average_cosine_similarity(hsv_average1, hsv_average2):
    cosine_similarity_values = []
    for avg1, avg2 in zip(hsv_average1, hsv_average2):
        vector_avg1 = np.array(avg1).flatten()
        vector_avg2 = np.array(avg2).flatten()
        similarity = cosine_similarity(vector_avg1, vector_avg2)
        cosine_similarity_values.append(similarity)
    average_cosine_similarity = np.mean(cosine_similarity_values)
    return average_cosine_similarity


# hsv_matrix1 = image_to_hsv_matrix('C:/Users/Hp/Documents/ALGEO 2/Algeo02-22036/static/uploads/test.jpg')
# hsv_average1 = hsv_average(hsv_matrix1)
# hsv_matrix2 = image_to_hsv_matrix('C:/Users/Hp/Documents/ALGEO 2/Algeo02-22036/static/uploads/test.jpg')
# hsv_average2 = hsv_average(hsv_matrix2)
# average_cosine_similarity = average_cosine_similarity(hsv_average1, hsv_average2)
# print(average_cosine_similarity)