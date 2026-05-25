from flask import Blueprint, render_template

inicio = Blueprint('inicio', __name__)

@inicio.route('/')
def index():
    return render_template('inicio.html')