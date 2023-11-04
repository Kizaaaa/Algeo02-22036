from PIL import Image
from feature_extract import FeatureExtract
from flask import Flask, request, render_template
from pathlib import Path
import numpy as np

app = Flask(__name__)

@app.route("/")

def index():
    return "TEST"

if __name__ == "__main__":
    app.run()