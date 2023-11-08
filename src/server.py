from PIL import Image
from feature_extract import FeatureExtract
from flask import Flask, request, render_template
from pathlib import Path
import numpy as np
import cv2 as cv
from datetime import datetime
app = Flask(__name__)

@app.route("/",methods=["GET","POST"])

def index():
    if(request.method == "POST"):
        return "File gambar diterima"
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run()