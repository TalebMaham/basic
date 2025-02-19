# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/test1')
def test1():
    return "Test 1 Passed"

@app.route('/test2')
def test2():
    return "Test 2 Passed"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
