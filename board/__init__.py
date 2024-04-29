# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:28:11 2024

@author: mduby
"""
import os
from dotenv import load_dotenv
from flask import Flask

from board import pages, entries, database

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    database.init_app(app)

    app.register_blueprint(pages.bp)
    app.register_blueprint(entries.bp)
    
    print(f"Current Environment: {os.getenv('ENVIRONMENT')}")
    print(f"Using Database: {app.config.get('DATABASE')}")
    return app