# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for

adm = Blueprint('admin', __name__)


@adm.route('/')
def admin_root():
    # do something
    return render_template('admin.html')
    

def index():
    return 'adm'

