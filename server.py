from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import image as CBIR
import shutil
import time
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
databaseDir = "static/imgdataset/"
app.secret_key = "secret key"
cacheDir = "static/cache/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
def clear_dir(directory):
    for dumpFiles in os.listdir(directory):
        os.remove(os.path.join(directory,dumpFiles))
@app.route('/')
def home():
    return render_template('home.html')
 
@app.route('/', methods=['POST'])
def upload_dataset():
    database = request.files.getlist("database")    
    databaseLoc = os.listdir(databaseDir)
    if database and any(f for f in database):
        clear_dir(databaseDir)
        clear_dir(cacheDir)
        isDatabaseValid = True
        for databasefiles in database:
            if(not allowed_file(databasefiles.filename)):
                isDatabaseValid = False
                break        
        if(isDatabaseValid):
            for databasefiles in database:
                datFileName = secure_filename(databasefiles.filename)
                databasefiles.save(os.path.join(databaseDir,datFileName))
            flash("Folder berhasil diunggah!\n")        
            databaseLocal = os.listdir(databaseDir)
            for databasefiles in databaseLocal:
                CBIR.save_cbir_results(os.path.join(databaseDir,databasefiles))
        else:
            flash('Folder yang Anda unggah mengandung file yang tidak valid. Silakan upload folder yang hanya mengandung file yang valid\n')
    else:
        flash('Tidak ada file di dalam folder yang dipilih\n')
    return upload_image()
def upload_image():
    #reset static database dan uploads
    start = time.time()
    clear_dir(UPLOAD_FOLDER)

    if 'file' not in request.files:
        flash('No file part\n')
        return redirect(request.url)
    file = request.files['file']


    if file.filename == '':
        flash('Tidak ada gambar yang dipilih\n')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Gambar berhasil diunggah!\n')
        imgPrioQueue = []
            #print(request.form.get('featuretoggle'))
        if(request.form.get('featuretoggle')):
            GLCM_Upload = CBIR.contrast_homogeneity_entropy(CBIR.image_to_normalized_glcm(UPLOAD_FOLDER+filename))
            for fileIterate in os.listdir(databaseDir):
                GLCM_avgDat = CBIR.get_cbir_results(os.path.join(databaseDir,fileIterate),'texture')
                print(GLCM_Upload)
                print(GLCM_avgDat)
                cosSim = CBIR.texture_cosine_similarity(GLCM_Upload,GLCM_avgDat) * 100
                print(cosSim)
                if(cosSim >60):
                    imgPrioQueue.append((cosSim,databaseDir+fileIterate))
        else:
            hsv_avgUpload = CBIR.hsv_average(CBIR.image_to_hsv_matrix(UPLOAD_FOLDER+filename))
            for fileIterate in os.listdir(databaseDir):
                hsv_avgDat = CBIR.get_cbir_results(os.path.join(databaseDir,fileIterate),'color')
                cosSim = CBIR.color_average_cosine_similarity(hsv_avgUpload,hsv_avgDat) * 100
                if(cosSim >60):
                    imgPrioQueue.append((cosSim,databaseDir+fileIterate))
            
        imgPrioQueue.sort(reverse=True)
        end = time.time()
        return render_template('home.html', filename=filename, imgPrioQueue=imgPrioQueue, prioQueueSize=len(imgPrioQueue),runTime = (end-start))
    else:
        flash('Ekstensi file yang diperbolehkan hanyalah .jpg, .png, dan .jpeg\n')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)