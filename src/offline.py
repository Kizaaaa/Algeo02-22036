from PIL import Image
from pathlib import  Path
import numpy as np
from feature_extract import FeatureExtract
if __name__ == "__main__":
    fe = FeatureExtract()
    for(imgpath) in  sorted(Path("./test/").glob("*.jpg")): #buat baca gambar di dataset
        print(imgpath)
        feature = fe.extract(img= Image.open(imgpath))
        featurepath = Path("./src/feature") / (imgpath.stem + ".npy")
        print(featurepath)
        np.save(featurepath,feature)