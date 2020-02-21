from flask import Flask, request,render_template,g
from werkzeug.utils import secure_filename
import sqlite3, datetime, os, random

DATABASE = 'test.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER

@app.route('/')
def index():
    boards = query_db('select * from boards')
    return render_template('homepage.html',boards=boards)

@app.route('/<board>')
def board(board):
    posts = query_db('select * from posts where board = "{}"'.format(board))
    return render_template('board.html',posts=posts,board=board)

@app.route('/<board>/post', methods = ['POST'])
def post(board):
    filename = ''
    if 'image' in request.files:
        upload_image(request.files['image'])
    now = datetime.datetime.now()
    post = (request.form.get('name'),now.isoformat(),board,request.form.get('post_text'),filename)
    print(create_post(post))
    return 'yay'

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

def create_post(request):
    query = ''' INSERT INTO posts(user, date, board, post_text,image_file) values (?,?,?,?,?) '''
    cur = get_db().cursor()
    cur.execute(query, request)
    get_db().commit()
    cur.close()
    return cur.lastrowid

def allowed_file(filename):
    return'.' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(image):
    filename=''
    if image and allowed_file(image.filename):
        print('image good')
        filename = secure_filename(image.filename)
        newfilename = str(random.randint(10000,100000))+'.'+filename.rsplit('.',1)[1].lower()
        image.save(os.path.join(app.config['UPLOAD_FOLDER'],newfilename))
    return newfilename
if __name__ == '__main__':
    app.run()
