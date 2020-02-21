from flask import Flask, request,render_template,g
from werkzeug.utils import secure_filename
import sqlite3, datetime, os, random

DATABASE = 'test.db'
UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER

@app.route('/')
def index():
    boards = query_db('select * from boards')
    return render_template('homepage.html',boards=boards)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


if __name__ == '__main__':
    app.run()
