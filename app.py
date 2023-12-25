from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'CHECKING AND REMOVING DUPLICATES FROM THE CHANNEL IS ACTIVATED AND IS PROGRESSING WELL....'


if __name__ == "__main__":
    app.run()
