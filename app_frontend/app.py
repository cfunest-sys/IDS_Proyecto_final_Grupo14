from flask import Flask
from routes.routes import inicio

PORT = 8080

app = Flask(__name__)
app.register_blueprint(inicio)

app.secret_key = "six_seven"

if __name__ == "__main__":
    app.run(debug=True, port=PORT)