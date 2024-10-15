from flask import render_template, redirect, url_for, send_from_directory
from flask_login import current_user
from models import Placas


def home():
    if current_user.is_authenticated:
        return render_template("home.html")
    else:
        return redirect(url_for('views.login'))


def cadastrar_os():
    placas = [row.to_dict() for row in Placas.query]
    return render_template("cadastrar_os.html", placas=placas)


def pesquisar():
    return render_template('pesquisar/pesquisar.html')


def serve_file(filename):
    return send_from_directory('', filename)


def health_check():
    return 'OK', 200
