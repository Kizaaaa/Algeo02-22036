if i - 1 >= 0 and j + 1 < cols:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i - 1, j + 1]] += 1
                glcm_matrix[grayscale_matrix[i - 1, j + 1], grayscale_matrix[i, j]] += 1
            if i + 1 < rows and j + 1 < cols:
                glcm_matrix[grayscale_matrix[i, j], grayscale_matrix[i + 1, j + 1]] += 1
                glcm_matrix[grayscale_matrix[i + 1, j + 1], grayscale_matrix[i, j]] += 1