from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import image as CBIR
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():
    return render_template('home.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    database = request.files.getlist("database")

    if file.filename == '':
        flash('Tidak ada gambar yang dipilih')
        return redirect(request.url)
    if not database or not any(f for f in database):
        flash('Tidak ada file di dalam folder yang dipilih')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Gambar berhasil diunggah!')
        isDatabaseValid = True
        for databasefiles in database:
            if(not allowed_file(databasefiles.filename)):
                isDatabaseValid = False
                break
        if(isDatabaseValid):
            databaseDir = "static/imgdataset/"
            for databasefiles in database:
                datFileName = secure_filename(databasefiles.filename)
                databasefiles.save(os.path.join(databaseDir,datFileName))
            flash("Folder berhasil diunggah!")
            hsv_avgUpload = CBIR.image_to_hsv_matrix(UPLOAD_FOLDER+filename)
            imgPrioQueue = []
            for fileIterate in os.listdir(databaseDir):
                hsv_avgDat = CBIR.image_to_hsv_matrix(databaseDir + fileIterate)
                cosSim = CBIR.color_average_cosine_similarity(hsv_avgUpload,hsv_avgDat) * 100
                
                if(cosSim >60):
                    imgPrioQueue.append((cosSim,databaseDir+fileIterate))
            imgPrioQueue.sort(reverse=True)

            
        else:
            flash('Folder yang Anda unggah mengandung file yang tidak valid. Silakan upload folder yang hanya mengandung file yang valid')
        return render_template('home.html', filename=filename, imgPrioQueue=imgPrioQueue)
    else:
        flash('Ekstensi file yang diperbolehkan hanyalah .jpg, .png, dan .jpeg')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)