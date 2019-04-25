from flask import Flask, request

app = Flask(__name__)


def create_feed_forward(content):
    pass

def create_rnn(content):
    pass

def create_cnn(content):
    pass

@app.route("/",methods=['POST'])
def handler():
    content = request.get_json()
    if content['nn_type'] == 'feedforward':
        create_feed_forward(content)
    elif content['nn_type'] == 'rnn':
        create_rnn(content)
    elif content['nn_type'] == 'cnn':
        create_cnn(content)
    else:
        return 'error!!!!'


if __name__ == "__main__":
    app.run()