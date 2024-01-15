from flask import Flask
import os
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'CHECKING AND REMOVING DUPLICATES FROM THE CHANNEL IS ACTIVATED AND IS PROGRESSING WELL....'


if __name__ == "__main__":
    #app.run()
    app.run(debug=True, port=os.getenv("PORT", default=8080), host='0.0.0.0')
