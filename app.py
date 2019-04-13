# import the nessecary pieces from Flask
from flask import Flask,render_template, request,jsonify,Response, flash, redirect
import os
import csv
from werkzeug.utils import secure_filename
#Create the app object that will route our calls
app = Flask(__name__)
# Add a single endpoint that we can use for testing


app.config["UPLOAD_DATA_FOLDER"]=app.instance_path + "/data/dataContent/"
app.secret_key="123789456"


@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/tabular_upload', methods = ['GET'])
def tabular_upload():
    return render_template('tabular_upload_singlefile.html')

@app.route('/tabular_upload', methods = ['POST'])
def tabular_upload_post():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        if(not os.path.isdir(app.config["UPLOAD_DATA_FOLDER"])):
            os.makedirs(app.config["UPLOAD_DATA_FOLDER"])
        filename = "training.txt"
        filepath = os.path.join(app.config["UPLOAD_DATA_FOLDER"], filename)
        file.save(filepath)
        if_ignore_1stline = request.form.get("ignoreHeader")
        if_target_category = request.form.get("categorical")
        size_input_neuron, size_output_neuron = tabular_getsize(filepath, if_target_category, if_ignore_1stline)
        print((if_target_category, if_ignore_1stline, size_input_neuron, size_output_neuron))
        return redirect("/?sizeInput=%d&sizeOutput=%d" %(size_input_neuron, size_output_neuron))

# return (size_input_neuron, size_output_neuron)
def tabular_getsize(filepath, if_target_category, if_ignore_1stline):
    n_feature = 0 
    n_output = 0
    set_labels = set()
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if(if_ignore_1stline):
                if_ignore_1stline = None
                continue
            n_feature = len(row)
            if(not if_target_category):
                n_output = 1
                return (n_feature, n_output)
            set_labels.add(row[-1])
    n_output = len(set_labels)
    return (n_feature, n_output)

#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
