# import the nessecary pieces from Flask
import sqlite3
from flask import current_app, g
from flask import Flask,render_template, request,jsonify,Response, flash, redirect
import os
import csv
import json
import gzip
from datetime import datetime
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
            file.save(filepath)
        size_input_neuron, size_output_neuron = tabular_getsize(filepath, if_target_category, if_ignore_1stline)
        print((if_target_category, if_ignore_1stline, size_input_neuron, size_output_neuron))
        lossfunc = "mse"
        if(if_target_category == "on"):
            lossfunc ="crossentropy"
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
            n_feature = len(row)
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
@app.route('/api/neural-network/v1.0/', methods = ['POST'])
def compile_model():
    content = request.get_json()
    if content['nn_type'] == 'feedforward':
        nn.create_feed_forward(content,"/Users/apple/Documents/SEM/SEM4/deep_learning/project/test_data_123/")
        return json.dumps({'status':'Compiled'})

    elif content['nn_type'] == 'rnn':
        nn.create_rnn(content,"/Users/apple/Documents/SEM/SEM4/deep_learning/project/test_data_123/")
        return json.dumps({'status':'Compiled'})
    else:
        return json.dumps({'status':'Compiled-Failed'})


@app.route('/images_upload', methods = ['GET'])
def images_upload():
    return render_template('image_upload.html')

@app.route("/images_upload", methods = ['POST'])
def images_upload_post():
    print("heloo")
    if 'inputfilePkl' in request.files:
        # upload pickle
        file = request.files['inputfilePkl']
        edir_pickle=app.config["UPLOAD_DATA_FOLDER"]+"/images/"
        if(not os.path.isdir(dir_pickle)):
            os.makedirs(dir_pickle)
        filepath = os.path.join(dir_pickle, "training.pickle")
        if(request.form.get("dataid")):
            images_savefile(file, request.form.get('dataid'), request.form.get('datadesc'), dir_pickle)
        else:
            file.save(filepath)
        sizes=images_getsize(filepath)
        print(sizes)
        if(isinstance(sizes, tuple)):
            size_input_neuron = sizes[1]*sizes[2]
            size_output_neuron = sizes[3]
            print("http://127.0.0.1:8080/index_cnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=1&regularizationRate=0&noise=0&networkShape=1,1,4,4&seed=0.35115&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, "crossentropy", filepath))
            return redirect("http://127.0.0.1:8080/index_cnn.html#activation=tanh&batchSize=10&dataset=circle&regDataset=reg-plane&learningRate=0.03&typeofnet=1&regularizationRate=0&noise=0&networkShape=1,1,4,4&seed=0.35115&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&discretize_hide=true&showTestData_hide=true&stepButton_hide=true&noise_hide=true&dataset_hide=true&sizeInput=%d&sizeOutput=%d&lossfunc=%s&dataLocation=%s" %(size_input_neuron, size_output_neuron, "crossentropy", filepath))
        else:
            return redirect(request.url)
    elif 'inputfilePNG' in request.files and 'inputfileCsv' in request.files:
        #
        return redirect(request.url)
    else:
        flash('No file part')
        return redirect(request.url)

    
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
            file.save(filepath)
        lossfunc="crossentropy"
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
    

#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
