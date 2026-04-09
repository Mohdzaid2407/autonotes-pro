from flask import Flask, render_template
from config import Config
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = "zaid_super_secret_key"

from routes.auth_routes import auth
from routes.main_routes import main

app.register_blueprint(auth)
app.register_blueprint(main)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)