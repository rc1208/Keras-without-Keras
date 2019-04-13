# import the nessecary pieces from Flask
from flask import Flask,render_template, request,jsonify,Response
#Create the app object that will route our calls
app = Flask(__name__)
# Add a single endpoint that we can use for testing

@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/tabular_upload', methods = ['GET'])
def tabular_upload():
    return render_template('tabular_upload.html')

#When run from command line, start the server
if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)
