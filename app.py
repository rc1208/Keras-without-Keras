# import the nessecary pieces from Flask
import sqlite3
from flask import current_app, g
from flask import Flask,render_template, request,jsonify,Response, flash, redirect
import os
import csv
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import make_response
from flask import abort
from tensorflow_serving.model_volume.neural_nets import nn
from flask_cors import CORS
#Create the app object that will route our calls
app = Flask(__name__)
CORS(app)
# Add a single endpoint that we can use for testing



app.config["UPLOAD_DATA_FOLDER"]=app.instance_path + "/data/"
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


@app.route("/images_upload", method = ["POST"])
#image upload: 
# if pkl/pklz, save as <data_id>.pklz, or <training_images>./pklz
# if pngs, mkdir images_temp/, upload to images_temp/, then convert to pklz
def images_upload_post():
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





#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
