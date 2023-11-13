from PIL import Image
import numpy as np

# Cosine Similarity
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

# CBIR dengan parameter warna
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

def color_average_cosine_similarity(image_path1, image_path2):
    hsv_average1 = image_to_hsv_matrix(image_path1)
    hsv_average2 = image_to_hsv_matrix(image_path2)
    cosine_similarity_values = []
    for avg1, avg2 in zip(hsv_average1, hsv_average2):
        vector_avg1 = np.array(avg1).flatten()
        vector_avg2 = np.array(avg2).flatten()
        similarity = cosine_similarity(vector_avg1, vector_avg2)
        cosine_similarity_values.append(similarity)
    average_cosine_similarity = np.mean(cosine_similarity_values)
    return average_cosine_similarity

# CBIR dengan parameter tesktur
def rgb_to_grayscale(r, g, b):
    y = 0.29 * r + 0.587 * g + 0.114 * b
    return y

def image_to_normalized_glcm(image_path):
    image = Image.open(image_path)
    rgb_matrix = np.array(image)
    grayscale_matrix = np.apply_along_axis(lambda pixel: int(round(rgb_to_grayscale(*pixel))), axis=-1, arr=rgb_matrix)
    glcm_matrix = np.zeros((256, 256), dtype=int)
    rows, cols = grayscale_matrix.shape
    for i in range(rows):
        for j in range(cols):
            if j + 1 < cols:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i, j + 1]] += 1
                glcm_matrix[grayscale_matrix[i, j + 1], grayscale_matrix[i, j]] += 1
            if i + 1 < rows:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i + 1, j]] += 1
                glcm_matrix[grayscale_matrix[i + 1, j], grayscale_matrix[i, j]] += 1
            if i - 1 >= 0 and j + 1 < cols:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i - 1, j + 1]] += 1
                glcm_matrix[grayscale_matrix[i - 1, j + 1], grayscale_matrix[i, j]] += 1
            if i + 1 < rows and j + 1 < cols:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i + 1, j + 1]] += 1
                glcm_matrix[grayscale_matrix[i + 1, j + 1], grayscale_matrix[i, j]] += 1
    symmetric_matrix = glcm_matrix + glcm_matrix.T
    sum = np.sum(symmetric_matrix)
    symmetric_matrix_normalized = symmetric_matrix / sum
    return symmetric_matrix_normalized

def contrast_homogeneity_entropy(symmetric_matrix_normalized):
    contrast = np.sum(symmetric_matrix_normalized * np.square(np.subtract.outer(range(256), range(256))))
    homogeneity = np.sum(symmetric_matrix_normalized / (1 + np.square(np.subtract.outer(range(256), range(256)))))
    entropy = -np.sum(symmetric_matrix_normalized * np.log2(symmetric_matrix_normalized + 1e-10))
    return contrast, homogeneity, entropy

def texture_cosine_similarity(image_path1, image_path2):
    symmetrix_matrix_normalized1 = image_to_normalized_glcm(image_path1)
    symmetrix_matrix_normalized2 = image_to_normalized_glcm(image_path2)
    contrast1, homogeneity1, entropy1 = contrast_homogeneity_entropy(symmetrix_matrix_normalized1)
    contrast2, homogeneity2, entropy2 = contrast_homogeneity_entropy(symmetrix_matrix_normalized2)
    vector1 = np.array([contrast1, homogeneity1, entropy1])
    vector2 = np.array([contrast2, homogeneity2, entropy2])
    cosine_similarity_value = cosine_similarity(vector1, vector2)
    return cosine_similarity_value

# image_path1 = 'C:/Users/Hp/Documents/ALGEO 2/Algeo02-22036/static/imgdataset/0.jpg'
# image_path2 = 'C:/Users/Hp/Documents/ALGEO 2/Algeo02-22036/static/imgdataset/4735.jpg'
# cosine_similarity = texture_cosine_similarity(image_path1, image_path2)
# print(cosine_similarity)