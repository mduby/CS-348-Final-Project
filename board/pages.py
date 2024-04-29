# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:36:00 2024

@author: mduby
"""

from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")

@bp.route("/logging")
def logging():
    return render_template("pages/logging.html")