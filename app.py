# import the nessecary pieces from Flask
import sqlite3
from flask import current_app, g
from flask import Flask,render_template, request,jsonify,Response, flash, redirect
from flask import send_file, send_from_directory
import os
import csv
import json
import gzip
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from flask import make_response
from flask import abort
from tensorflow_serving.model_volume.neural_nets import nn
from flask_cors import CORS
import pickle
#Create the app object that will route our calls
app = Flask(__name__)
CORS(app)
# Add a single endpoint that we can use for testing



app.config["DATA_FOLDER"]=app.instance_path + "/data/"
app.config["UPLOAD_DATA_FOLDER"]=app.config["DATA_FOLDER"]+"/upload/"
app.config["CALLBACK_LOG_FOLDER"]=app.config["DATA_FOLDER"]+"/logcsv/"
app.secret_key="123789456"
app.config["DATABASE"] = app.instance_path + "/data.db"
app.config["DBTABLE_DATA"] = "training_data"

app.config["LOSS_TABULAR_CATEGORY"] = "categorical_crossentropy"
app.config["LOSS_TABULAR_NUMERIC"] = "mse"
app.config["LOSS_IMAGES"] = "categorical_crossentropy"
app.config["LOSS_TEXT"] = "categorical_crossentropy"

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
        filepath = os.path.join(app.config["UPLOAD_DATA_FOLDER"], "training.csv")
        if(request.form.get("dataid")):
            tabular_savefile(file, request.form.get('dataid'), request.form.get('datadesc'),  if_ignore_1stline, if_target_category)
        else:
            if(os.path.exists(filepath)):
                os.remove(filepath)
            file.save(filepath)
        size_input_neuron, size_output_neuron = tabular_getsize(filepath, if_target_category, if_ignore_1stline)
        print((if_target_category, if_ignore_1stline, size_input_neuron, size_output_neuron))
        lossfunc = app.config["LOSS_TABULAR_NUMERIC"]
        if(if_target_category == "on"):
            lossfunc =app.config["LOSS_TABULAR_CATEGORY"]
        return redirect("http://127.0.0.1:8080/#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&regularizationRate=0&noise=0&networkShape=3,2&seed=0.44887&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, lossfunc, filepath))



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
            n_feature = len(row) - 1
            if(not if_target_category):
                n_output = 1
                return (n_feature, n_output)
            set_labels.add(row[-1])
    n_output = len(set_labels)
    return (n_feature, n_output)





#
def tabular_savefile(file, data_id, data_desc, if_ignore_1stline, if_target_category):
    #save the file (name as data_id), and link to "training.csv"
    filepath = os.path.join(app.config["UPLOAD_DATA_FOLDER"], data_id)
    file.save(filepath)
    training_file=os.path.join(app.config["UPLOAD_DATA_FOLDER"], "training.csv")
    if(os.path.exists(training_file)):
        os.remove(training_file)
    os.symlink(filepath, training_file)
    #save file info to db
    conn = get_db()
    conn.execute('''
    insert into %s (id, type, description, date_created, file_number, if_ignore_1stline, if_target_category) values (?,?,?,?,?,?,?)''' %app.config["DBTABLE_DATA"], \
                 (data_id, "tabular", data_desc, datetime.now().strftime("%Y-%m-%d %H-%M-%S"), 1, if_ignore_1stline, if_target_category) )
    conn.commit()




def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

'''@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
'''
@app.route('/check_dataid_ok/<dataid>', methods=["POST", "GET"])
def check_dataid_existence(dataid):
    db=get_db()
    sqlcmd = "SELECT * FROM training_data WHERE id = ?"
    print(sqlcmd)
    cur=db.execute(sqlcmd, (dataid,))
    rv = cur.fetchone()
    if(rv is None):
        return 'SUCCESS'
    else:
        return 'FAIL'

### -------API Design ----- ####

### function to handle error response ###
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#### dummy data ####
tasks = [
    {
        'id': 1,
        'done': False
    },
    {
        'id': 2,
        'done': False
    },
    {
        'id': 2,
        'done': True
    }
]

### experimental GET function. Get rid of this in the final architecture ###
@app.route('/api/v1.0/tasks/<int:task_id>', methods=['POST'])
def get_tasks(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)

    return jsonify({'task': task[1]})

### feedforward NN API - GET request at 1 - make the model with the given id '1' and data file

def return_json(file):
    ret = pd.read_csv(file)
    if ret.empty:
        return json.dumps({'status': 'model training failed'})
    return ret.to_json()


@app.route('/api/neural-network/v1.0/', methods = ['POST'])
def compile_model():
    content = request.get_json()
    filename = ""
    if content['nn_type'] == 'feedforward':
        filename = nn.create_feed_forward(content,"data/mse")
        return return_json(filename)

    elif content['nn_type'] == 'rnn':
        filename = nn.create_rnn(content,"data/mse")
        print(filename)
        return return_json(filename)

    elif content['nn_type'] == 'cnn':
        filename = nn.create_cnn(content,"data/mse")
        return return_json(filename)

    else:
        return json.dumps({'status':'unknown model expected'})


@app.route('/images_upload', methods = ['GET'])
def images_upload():
    return render_template('image_upload.html')

@app.route("/images_upload", methods = ['POST'])
def images_upload_post():
    print("heloo")
    if 'inputfilePkl' in request.files:
        # upload pickle
        file = request.files['inputfilePkl']
        dir_pickle=app.config["UPLOAD_DATA_FOLDER"]+"/images/"
        if(not os.path.isdir(dir_pickle)):
            os.makedirs(dir_pickle)
        filepath = os.path.join(dir_pickle, "training.pickle")
        if(request.form.get("dataid")):
            images_savefile(file, request.form.get('dataid'), request.form.get('datadesc'), dir_pickle)
        else:
            if(os.path.exists(filepath)):
                os.remove(filepath)
            file.save(filepath)
        pickle_gzip(file.filename, filepath)
        sizes=images_getsize(filepath)
        print(sizes)
        if(isinstance(sizes, tuple)):
            size_input_neuron = sizes[1]*sizes[2]
            size_output_neuron = sizes[3]
            print("http://127.0.0.1:8080/index_cnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=1&regularizationRate=0&noise=0&networkShape=1,1,4,4&seed=0.35115&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, app.config["LOSS_IMAGES"], filepath))
            return redirect("http://127.0.0.1:8080/index_cnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=1&regularizationRate=0&noise=0&networkShape=1,1,4,4&seed=0.35115&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, app.config["LOSS_IMAGES"], filepath))
        else:
            return redirect(request.url)
    elif 'inputfilePNG' in request.files and 'inputfileCsv' in request.files:
        #
        return redirect(request.url)
    else:
        flash('No file part')
        return redirect(request.url)

# if upload_filename is *.pklz, ignore; if upload_filename is *.pkl, read data from "save_filename" & re-write as "zip pickle"
def pickle_gzip(upload_filename, save_filename): 
    if(upload_filename[-1] == "z"):
        return
    else:
        with open(save_filename, "rb") as f:
            data = pickle.load(f)
        with gzip.open(save_filename, "wb") as f:
            pickle.dump(data, f, 1)

def images_savefile(file, data_id, data_desc, dir_pickle):
    #save the file (name as data_id), and link to "training.csv"
    filepath = os.path.join(dir_pickle, data_id)
    file.save(filepath)
    training_file=os.path.join(dir_pickle, "training.pickle")
    if(os.path.exists(training_file)):
        os.remove(training_file)
    os.symlink(filepath, training_file)
    #save file info to db
    conn = get_db()
    conn.execute('''
    insert into %s (id, type, description, date_created, file_number, if_ignore_1stline, if_target_category) values (?,?,?,?,?,?,?)''' %app.config["DBTABLE_DATA"], \
                 (data_id, "images", data_desc, datetime.now().strftime("%Y-%m-%d %H-%M-%S"), 1, 0, 0) )
    conn.commit()

def images_getsize(pickle_path):
    print(pickle_path)
    with gzip.open(pickle_path, "rb") as f:
        data=pickle.load(f)
        if(len(data) < 2):
            return "DataFormatError"
        if(len(data[0].shape) != 3):
            return "DataFormatError"
        n_image,width,height = data[0].shape
        if(data[1].shape[0] != data[0].shape[0]):
            return "DataFormatError"
        if(len(data[1].shape) == 1):
            setx = set(data[1])
        elif( len(data[1].shape)==2 and  data[1].shape[1] == 1):
            setx=set(data[1].flatten())
        else:
            return "DataFormatError"
        n_class=len(setx)
        return (n_image, width, height, n_class)


@app.route('/text_upload', methods = ['GET'])
def text_upload():
    return render_template('text_upload.html')

@app.route("/text_upload", methods = ['POST'])
def text_upload_post():
    if 'inputfileText' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['inputfileText']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        dir_text=app.config["UPLOAD_DATA_FOLDER"]+"/text/"
        if(not os.path.isdir(dir_text)):
            os.makedirs(dir_text)
        filepath = os.path.join(dir_text, "training.txt")
        if(request.form.get("dataid")):
            text_savefile(file, request.form.get('dataid'), request.form.get('datadesc'), dir_text)
        else:
            if(os.path.exists(filepath)):
                os.remove(filepath)
            file.save(filepath)
        lossfunc=app.config["LOSS_TEXT"]
        return redirect("http://127.0.0.1:8080/index_rnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=2&regularizationRate=0&noise=0&networkShape=1&seed=0.09947&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&lossfunc=%s&dataLocation=%s" %(lossfunc, filepath))

def text_savefile(file, data_id, data_desc, dir_text):
    filepath = os.path.join(dir_text, data_id)
    file.save(filepath)
    training_file=os.path.join(dir_text, "training.txt")
    if(os.path.exists(training_file)):
        os.remove(training_file)
    os.symlink(filepath, training_file)
    #save file info to db
    conn = get_db()
    conn.execute('''
    insert into %s (id, type, description, date_created, file_number, if_ignore_1stline, if_target_category) values (?,?,?,?,?,?,?)''' %app.config["DBTABLE_DATA"], \
                 (data_id, "text", data_desc, datetime.now().strftime("%Y-%m-%d %H-%M-%S"), 1, 0, 0) )
    conn.commit()

@app.route("/data_list/<typex>", methods=["GET"])
def show_data_list(typex):
    datalist=get_data_list(typex)
    rows=[]
    for dataitem in datalist:
        row=dict()
        row["dataid"] = dataitem["id"]
        row["datadesc"] = dataitem["description"]
        row["type"] = dataitem["type"]
        row["date"] = dataitem["date_created"]
        if(row["type"] == "tabular"):
            if(dataitem["if_target_category"] == "on"):
                row["note"] = "Classification"
                row["lossfunc"] =  app.config["LOSS_TABULAR_CATEGORY"]
            else:
                row["note"] = "Regression"
                row["lossfunc"] =  app.config["LOSS_TABULAR_NUMERIC"]
        elif(row["type"] == "images"):
            row["note"] = "Classification"
            row["lossfunc"] =  app.config["LOSS_IMAGES"]
        else:
            row["note"] = "Language Model"
            row["lossfunc"] = app.config["LOSS_TEXT"]
        row["url"] = "/download_data/%s/%s" %(row["type"], row["dataid"])
        row["data_location"] = get_data_dir(row["type"], row["dataid"]) + "/" + row["dataid"]
        rows.append(row)
    return render_template("list_data_template.html", data=rows)


def get_data_list(typex):
    db=get_db()
    if(typex == "all"):
        sqlcmd = "SELECT * FROM training_data"
    else:
        sqlcmd = "SELECT * FROM training_data where type = '%s'" %typex
    print(sqlcmd)
    cur=db.execute(sqlcmd)
    rv = cur.fetchall()
    return rv

def get_data_dir(typex, dataid):
    if(typex == "tabular"):
        dirx = app.config["UPLOAD_DATA_FOLDER"] + "/"
    elif(typex == "images"):
        dirx = app.config["UPLOAD_DATA_FOLDER"] + "/images/"
    else:
        dirx = app.config["UPLOAD_DATA_FOLDER"] + "/text/"
    return dirx

@app.route("/download_data/<typex>/<dataid>", methods = ['GET'])
def download_file(typex, dataid):
    print("download_file")
    dirx = get_data_dir(typex, dataid)
    print(dataid)
    return send_from_directory(dirx, dataid, as_attachment=True) 

@app.route("/data_select", methods = ['POST'])
def use_data_nn():
    typex = request.form.get("type")
    data_location = request.form.get("data_location")
    lossfunc = request.form.get("lossfunc")
    task = request.form.get("task")
    if(typex == "tabular"):
        if(task == "Classification"):
            size_input_neuron, size_output_neuron = tabular_getsize(data_location, 1, 1)
        else:
            size_input_neuron, size_output_neuron = tabular_getsize(data_location, 0, 1)
        print((size_input_neuron, size_output_neuron))
        return redirect("http://127.0.0.1:8080/#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&regularizationRate=0&noise=0&networkShape=3,2&seed=0.44887&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, lossfunc, data_location))
    elif(typex == "images"):
        sizes=images_getsize(data_location)
        if(isinstance(sizes, tuple)):
            size_input_neuron = sizes[1]*sizes[2]
            size_output_neuron = sizes[3]
            return redirect("http://127.0.0.1:8080/index_cnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=1&regularizationRate=0&noise=0&networkShape=1,1,4,4&seed=0.35115&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, app.config["LOSS_IMAGES"], data_location))
        else:
            return redirect(request.url)
    else:
        return redirect("http://127.0.0.1:8080/index_rnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=2&regularizationRate=0&noise=0&networkShape=1&seed=0.09947&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&lossfunc=%s&dataLocation=%s" %(lossfunc, data_location))

        

#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
