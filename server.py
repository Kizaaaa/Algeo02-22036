from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import urllib.request
import os
from werkzeug.utils import secure_filename
import image as CBIR
import shutil
import time
from flask_paginate import get_page_args,Pagination
from fpdf import FPDF
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
databaseDir = "static/imgdataset/"
downloadDir = "static/downloads/"
app.secret_key = "secret key"
cacheDir = "static/cache/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#list temporary untuk pagination
imgPrioQueue = []
inputRuntime = []
uploadedImage = []
chosenParameter =[]
tempIMGPQ = []
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
def clear_dir(directory):
    for dumpFiles in os.listdir(directory):
        os.remove(os.path.join(directory,dumpFiles))
def get_img(offset=0,per_page=8):
    return imgPrioQueue[offset: offset+per_page]
@app.route('/')
def home():
    page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
    total = len(imgPrioQueue)
    pagination_img = get_img(offset=offset,per_page=per_page)
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')

    if(len(uploadedImage) == 0):
        filename = ''
    else:
        filename=uploadedImage[0]
    if(len(inputRuntime) == 0):
        runTime = 0
    else:
        runTime = inputRuntime[0]
    return render_template('index.html', filename=filename, imgPrioQueue=pagination_img, page=page, per_page=per_page, pagination=pagination,prioQueueSize = total, runTime=runTime)
 
@app.route('/', methods=['POST'])
def upload_dataset():
    start = time.time()
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
            flash('Folder yang Anda unggah mengandung file yang tidak valid. Silakan upload folder yang hanya mengandung file yang valid, yaitu .png, .jpg, .jpeg, atau .bmp.\n')
        end = time.time()
        flash('Waktu pengunggahan dataset yang berisi ' + str(len(databaseLocal)) + ' gambar adalah '+str(end-start)+' detik')
    else:
        flash('Tidak ada file di dalam folder dataset yang dipilih\n')

    return upload_image()
def upload_image():
    #reset static database dan uploads
    start = time.time()
    clear_dir(UPLOAD_FOLDER)
    imgPrioQueue.clear()
    inputRuntime.clear()
    uploadedImage.clear()
    chosenParameter.clear()
    if 'file' not in request.files:
        flash('No file part\n')
        return redirect(request.url)
    file = request.files['file']


    if file.filename == '':
        flash('Tidak ada gambar query yang diunggah\n')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Gambar berhasil diunggah!\n')
        uploadedImage.append(filename)
            #print(request.form.get('featuretoggle'))
        if(request.form.get('featuretoggle')):
            chosenParameter.append("Tekstur")
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
            chosenParameter.append("Warna")
            hsv_avgUpload = CBIR.hsv_average(CBIR.image_to_hsv_matrix(UPLOAD_FOLDER+filename))
            for fileIterate in os.listdir(databaseDir):
                hsv_avgDat = CBIR.get_cbir_results(os.path.join(databaseDir,fileIterate),'color')
                cosSim = CBIR.color_average_cosine_similarity(hsv_avgUpload,hsv_avgDat) * 100
                if(cosSim >60):
                    imgPrioQueue.append((cosSim,databaseDir+fileIterate))
            
        imgPrioQueue.sort(reverse=True)
        end = time.time()
        inputRuntime.append(end-start)
        return home()
        #render_template('home.html', filename=filename, imgPrioQueue=imgPrioQueue,prioQueueSize = len(imgPrioQueue), runTime=(end-start))
    else:
        flash('Ekstensi file yang diperbolehkan hanyalah .jpg, .png, .jpeg, atau .bmp\n')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/download',methods=['GET'])
def download_file():
    tempIMGPQ = imgPrioQueue
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('arial','B',20)
    pdf.cell(h=20,w=190,border=0,txt="Never Gonna Lens You Up",align="C",ln=1)
    pdf.set_font('arial',size=16)
    pdf.cell(h=20,w=190,border=0,txt="Website pencarian gambar dengan metode CBIR warna dan tekstur",ln=1,align="C")
    pdf.cell(h=20,w=190,border=0,txt="Parameter yang dipilih: "+chosenParameter[0],ln=1,align="L")
    pdf.cell(h=150,w=190,border=1,txt="Gambar Query: ",ln=1,align="L")
    pdf.image(UPLOAD_FOLDER+uploadedImage[0],w=100,x=80,y=80)
    pdf.cell(h=20,w=190,border=0,txt="Banyak Gambar yang ditemukan: "+str(len(tempIMGPQ)),ln=1,align="L")
    pdf.cell(h=20,w=190,border=0,txt="Waktu eksekusi: "+str(inputRuntime[0])+" detik",ln=1,align="L")
    i = 0
    pdf.set_font('arial','B',18)
    pdf.cell(h=20,w=190,border=0,txt="Tabel Data Kemiripan Gambar Dataset dengan Gambar Query",ln=1,align="C")
    
    for images in tempIMGPQ:
        if(i%5 == 0):
            if(i!=0):
                pdf.add_page()
            pdf.set_font('arial','B',16)
            pdf.cell(h=10,w=10,border=1,txt="No.",ln=0,align="C")
            pdf.cell(h=10,w=100,border=1,txt="Gambar",ln=0,align="C")
            pdf.cell(h=10,w=80,border=1,txt="Kemiripan dengan query (%)",ln=1,align="C")
        pdf.set_font('arial',size=16)
        pdf.cell(h=10,w=10,border=1,txt=str(i+1),ln=0,align="C")
        pdf.cell(h=10,w=100,border=0,ln=0,align="C",link=pdf.image(images[1],w = 40))
        pdf.cell(h=10,w=80,border=1,txt=str(images[0]),ln=1,align="C")
        
        i+=1

    p = downloadDir+"ImageRetrievalResult.pdf"
    pdf.output(p,'F')
    return send_file(p,as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)