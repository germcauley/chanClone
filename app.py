from flask import Flask,redirect, request, render_template, g
from werkzeug.utils import secure_filename
import sqlite3, datetime, os, random

DATABASE = 'test.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


def create_new_post(request, reply_id):
    print('reply id is: '+str(reply_id))

    if reply_id == 0:
        query = ''' INSERT INTO posts(image_file, user, date, board, post_text) values (?,?,?,?,?) '''
    else:
        query = ''' INSERT INTO replies(image_file, user, date, board, post_text, replying_to) values (?,?,?,?,?,?) '''
    cur = get_db().cursor()
    cur.execute(query, (request),)
    get_db().commit()
    cur.close()
    return cur.lastrowid


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    boards = query_db('select * from boards')
    return render_template('homepage.html', boards=boards)


@app.route('/<board>')
def board(board):
    posts = query_db('select * from posts where board = "{}"'.format(board))
    return render_template('board.html', posts=posts, board=board)


@app.route('/<board>/post', methods=['POST'])
def post(board):
    newfilename = ''
    if request.form.get('post_text'):
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                print('file good')
                filename = secure_filename(file.filename)
                newfilename = str(random.randint(10000000, 100000000)) + '.' + filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
        now = datetime.datetime.now()
        post = (newfilename, request.form.get('name'), now.isoformat(), board, request.form.get('post_text'), '0')
        print(create_new_post(post, '0'))
    return redirect('/')


@app.route('/<board>/post_reply/<post_id>', methods = ['POST'])
def post_reply(board,post_id):
    newfilename=''
    if request.form.get('post_text'):
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                print("file good")
                filename = secure_filename(file.filename)
                newfilename = str(random.randint(10000000,100000000))+'.'+filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
        now = datetime.datetime.now()
        post = (newfilename,request.form.get('name'),now.isoformat(),board,request.form.get('post_text'),post_id)
        print(create_new_post(post,post_id))
    return 'posted'

@app.route('/<board>/reply/<post_id>')
def reply(board, post_id):
    post = query_db('select * from posts where post_id = {}'.format(post_id))
    replies = query_db('select * from replies where replying_to = "{}"'.format(post_id))
    print(replies)
    return render_template('reply.html',post=post[0],replies=replies,board=board)


def upload_image(image):
    if image and allowed_file(image.filename):
        print('image good')
        filename = secure_filename(image.filename)
        newfilename = str(random.randint(10000, 100000)) + '.' + filename.rsplit('.', 1)[1].lower()
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename))
        print(newfilename)
        return newfilename


if __name__ == '__main__':
    app.run()
