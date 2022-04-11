from flask import Flask

app = Flask(__name__)

from flask import url_for

@app.route('/')
def index():
    return 'index'

@app.route('/login')
def login():
    return 'login'

@app.route('/user/<username>')
def profile(username):
    return f'{username}\'s profile'

# Pour tester
with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))

if __name__ == "__main__":
    app.run(port=8000)
# A run dans bash
# As a shortcut, if the file is named app.py or wsgi.py, you don’t have to set the FLASK_APP environment variable
# export FLASK_APP=app
# flask run

# export FLASK_ENV=development
# To enable all development features, set the FLASK_ENV environment variable to development before calling flask run.