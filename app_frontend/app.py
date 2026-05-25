from flask import Flask
from routes.routes import inicio

PORT = 8080

app = Flask(__name__)
app.register_blueprint(inicio)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)