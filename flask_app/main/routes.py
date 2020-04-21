from flask import Blueprint, render_template

main = Blueprint('main', '__name__')


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('base.html')


@main.route('/about2')
def about2():
    return render_template('about2.html')
