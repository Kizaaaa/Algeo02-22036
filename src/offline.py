import cv2 as cv
from pathlib import Path
import numpy as np
from feature_extract import FeatureExtract
from PIL import Image
if __name__ == "__main__":
    fe = FeatureExtract()
    for imgpath in sorted(Path("./test").glob("*.jpg")):
        print(imgpath)
        feature = fe.extract(img=Image.open(imgpath))
        print(type(feature), feature.shape)
        featurepath = Path("./src/feature")/(imgpath.stem + ".npy")
        #print(featurepath)
        np.save(featurepath,feature)