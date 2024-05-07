from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for
from utils import configuration

home = Blueprint('home', __name__)


@home.route('/home')
def land():
    return render_template("home/home.html", 
                           pconfig=configuration.get_vars()['DEFAULT'])