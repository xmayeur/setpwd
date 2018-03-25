# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for

adm = Blueprint('admins', __name__)


@adm.route('/')
def admin_root():
    # do something
    return render_template('admins.html')
    

def index():
    return 'adm'

