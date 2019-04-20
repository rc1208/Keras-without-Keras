# import the nessecary pieces from Flask
from flask import Flask,render_template, request,jsonify,Response, flash, redirect
import os
import csv
import json
from datetime import datetime
from werkzeug.utils import secure_filename
#Create the app object that will route our calls
app = Flask(__name__)
# Add a single endpoint that we can use for testing


app.config["UPLOAD_DATA_FOLDER"]=app.instance_path + "/data/dataContent/"
app.config["UPLOAD_INVECTORY_FOLDER"]=app.instance_path + "/data/dataInventory/"
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
        if_ignore_1stline = request.form.get("ignoreHeader")
        if_target_category = request.form.get("categorical")
        filepath = os.path.join(app.config["UPLOAD_DATA_FOLDER"], "training.txt")
        if(request.form.get("dataid")):
            tabular_savefile(file, request.form.get('dataid'), request.form.get('datadesc'),  if_ignore_1stline, if_target_category)
        else:
            file.save(filepath)
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

#
def tabular_savefile(file, file_id, file_description, if_ignore_1stline, if_target_category):
    # save the file into fileid, save the inventory, link file to training.txt
    filepath = os.path.join(app.config["UPLOAD_DATA_FOLDER"], file_id)
    file.save(filepath)
    training_file=os.path.join(app.config["UPLOAD_DATA_FOLDER"], "training.txt")
    if(os.path.exists(training_file)):
        os.remove(training_file)
    os.symlink(filepath, training_file)
    if(not os.path.isdir(app.config["UPLOAD_INVECTORY_FOLDER"])):
        os.makedirs(app.config["UPLOAD_INVECTORY_FOLDER"])
    invpath = os.path.join(app.config["UPLOAD_INVECTORY_FOLDER"], file_id)
    inv_dict = dict()
    inv_dict["data_id"] = file_id
    now=datetime.now()
    strdate = now.strftime("%Y-%m-%d %H-%M-%S")
    inv_dict["dated_created"] = strdate
    inv_dict["data_type"] = "tabular"
    inv_dict["file_number"] = 1
    inv_dict["data_description"] = file_description
    inv_dict["if_ignore_1stline"] = if_ignore_1stline
    inv_dict["if_target_category"] = if_target_category
    with open(invpath, "w") as f:
        json.dump(inv_dict, f)


#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
