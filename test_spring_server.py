
from flask import Flask
from flask import request
import json as JSON
import datetime
app = Flask(__name__)

user = {'ji': '2004',
        'juan': '2003'}


@app.route('/login', methods=['POST'])
def login():
    request_json = JSON.loads(request.data)
    print(request_json)
    if request_json and request_json['username'] and request_json['password']:
        if request_json['username'] in user and \
                        request_json['password'] == user[request_json['username']]:
            return 'succ'
    return 'fail'


@app.route('/register', methods=['POST'])
def register():
    request_json = JSON.loads(request.data)
    print(request_json)
    if request_json and request_json['username'] and request_json['password']:
        if request_json['username'] not in user:
            user[request_json['username']] = request_json['password']
            return 'succ'
    return 'fail'

def test():
    start_date = datetime.datetime.now() + datetime.timedelta(days=30)
    print(start_date)
    print(type(start_date))

if __name__ == '__main__':
    # app.run(debug=True, port=8889)
    test()


