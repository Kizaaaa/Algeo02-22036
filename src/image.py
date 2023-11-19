from PIL import Image
import numpy as np
import os

# Cosine Similarity
def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b)) #nilai dot product dari vektor a dan vektor b
    norm_a = sum(a**2 for a in vector_a) ** 0.5 #nilai vektor a yang sudah dinormalisasi
    norm_b = sum(b**2 for b in vector_b) ** 0.5 #nilai vektor a yang sudah dinormalisasi
    if norm_a == 0 and norm_b == 0: #jika normalisasi vektor a = normalisasi vektor b = 0
        return 1.0 #kembalikan nilai 1 karena vektor a dan b sudah pasti berimpit
    elif norm_a == 0 or norm_b == 0: #jika hanya salah satunya yang bernilai 0
        return 0.0 #kembalikan nilai 0 karena nilai dot productnya adalah 0
    cosine_similarity_value = dot_product / (norm_a * norm_b) #hitung cosine similarity
    return cosine_similarity_value

# CBIR dengan parameter warna
def rgb_to_hsv(rgb_tuple): #mengubah RGB menjadi HSV
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

def image_to_hsv_matrix(image_path): #mengubah gambar menjadi matriks HSV
    image = Image.open(image_path).convert("RGB")
    resized_image = image.resize((256, 256)) #resize gambar menjadi 256x256
    rgb_matrix = np.array(resized_image)
    hsv_matrix = np.array([[rgb_to_hsv(pixel) for pixel in row] for row in rgb_matrix]) 
    #ubah matriks RGB menjadi HSV
    return hsv_matrix

def hsv_average(hsv_matrix): #menghitung 16 buah vektor yang berisi rata-rata nilai H,S,dan V
    rows, cols, _ = hsv_matrix.shape
    part_rows = rows // 4 #bagi matriks menjadi 4x4 blok
    part_cols = cols // 4 #bagi matriks menjadi 4x4 blok
    hsv_average = [] #16 vektor rata-rata nilai HSV akan disimpan di sini
    for i in range(4):
        for j in range(4):
            part = hsv_matrix[i * part_rows : (i + 1) * part_rows, j * part_cols : (j + 1) * part_cols] 
            #pilih blok yang akan dihitung vektor rata-rata nilai HSV nya
            average_h = round(np.mean(part[:, :, 0]), 2) #hitung rata-rata nilai H dari blok yang dipilih
            average_s = round(np.mean(part[:, :, 1]), 2) #hitung rata-rata nilai S dari blok yang dipilih
            average_v = round(np.mean(part[:, :, 2]), 2) #hitung rata-rata nilai V dari blok yang dipilih
            hsv_average.append((average_h, average_s, average_v)) #simpan ke list 
    return hsv_average

def color_average_cosine_similarity(hsv_average1, hsv_average2):
    cosine_similarity_values = [] #nilai cosine similarity dari 16 blok akan diletakkan di list ini
    for avg1, avg2 in zip(hsv_average1, hsv_average2):
        vector_avg1 = np.array(avg1).flatten()
        vector_avg2 = np.array(avg2).flatten()
        similarity = cosine_similarity(vector_avg1, vector_avg2) #hitung nilai cosine similarity dari dua buah vektor yang bersesuaian
        cosine_similarity_values.append(similarity) #simpan nilai tersebut ke list
    average_cosine_similarity = np.mean(cosine_similarity_values) #hitung rata-rata nilai cosine similarity dari semua blok
    return average_cosine_similarity 

# CBIR dengan parameter tesktur
def rgb_to_grayscale(r, g, b): #mengubah RGB menjadi grayscale
    y = 0.29 * r + 0.587 * g + 0.114 * b
    return y

def image_to_normalized_glcm(image_path):
    #sudut yang dipilih adalah 0 derajat dan 90 derajat
    image = Image.open(image_path).convert("RGB")
    resized_image = image.resize((256, 256))
    rgb_matrix = np.array(resized_image)
    grayscale_matrix = np.apply_along_axis(lambda pixel: int(round(rgb_to_grayscale(*pixel))), axis=-1, arr=rgb_matrix) 
    #ubah gambar menjadi matriks grayscale
    #susun matriks GLCM
    glcm_matrix = np.zeros((256,256), dtype=int)
    right_neighbors = np.roll(grayscale_matrix, shift=-1, axis=1)
    down_neighbors = np.roll(grayscale_matrix, shift=-1, axis=0)
    glcm_matrix[grayscale_matrix, right_neighbors] += 1
    glcm_matrix[right_neighbors, grayscale_matrix] += 1
    glcm_matrix[grayscale_matrix, down_neighbors] += 1
    glcm_matrix[down_neighbors, grayscale_matrix] += 1
    symmetric_matrix = glcm_matrix + glcm_matrix.T #hitung symmetric matrix
    symmetric_matrix_normalized = symmetric_matrix / np.sum(symmetric_matrix) #normalisasi symmetry matrix
    return symmetric_matrix_normalized

def contrast_homogeneity_entropy(symmetric_matrix_normalized):
    contrast = np.sum(symmetric_matrix_normalized * np.square(np.subtract.outer(range(256), range(256)))) #hitung nilai contrast
    homogeneity = np.sum(symmetric_matrix_normalized / (1 + np.square(np.subtract.outer(range(256), range(256))))) #hitung nilai homogeneity
    entropy = -np.sum(symmetric_matrix_normalized * np.log2(symmetric_matrix_normalized + 1e-10)) #hitung nilai entropy
    return contrast, homogeneity, entropy

def texture_cosine_similarity(v1, v2): #hitung nilai cosine similarity
    vector1 = list(v1)
    vector2 = list(v2)
    cosine_similarity_value = cosine_similarity(vector1, vector2) 
    return cosine_similarity_value

# File Handling
def save_cbir_results(image_path): #simpan semua vektor sebagai cache
    hsv_matrix = image_to_hsv_matrix(image_path)
    text_file_path = "static/cache/"+ os.path.splitext(os.path.basename(image_path))[0] + '.txt'

    hsv_average_result = hsv_average(hsv_matrix)
    glcm_matrix_normalized = image_to_normalized_glcm(image_path)
    contrast, homogeneity, entropy = contrast_homogeneity_entropy(glcm_matrix_normalized)
    glcm_result = (contrast, homogeneity, entropy)

    with open(text_file_path, 'w') as file:
        file.write('\t'.join(map(str, hsv_average_result)) + '\n')
        file.write('\t'.join(map(str, glcm_result)) + '\n')

def get_cbir_results(image_path, cbir_type): #muat file cache
    text_file_path = "static/cache/"+ os.path.splitext(os.path.basename(image_path))[0] + '.txt'
    with open(text_file_path, 'r') as file:
        lines = file.readlines()
    if cbir_type == "color":
        result_color = lines[0].strip().split('\t')
        result_color_out = [eval(i) for a,i in enumerate(result_color)]

        return result_color_out
    else:
        result_texture = lines[1].strip().split('\t')

        return float(result_texture[0]), float(result_texture[1]), float(result_texture[2])

