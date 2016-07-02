# taken from minitwit
import os
import time
import ConfigParser
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5, sha256     # TODO: md5 doesn't get used 
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, \
     send_file, send_from_directory, app                    # this is for file downloads
from werkzeug import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename 

# google stuff right here 
import json
import httplib2
from apiclient import discovery
from oauth2client import client

# dropbox stuff 
from dropbox.client import DropboxOAuth2Flow, DropboxClient
import dropbox # do i need this any more?

# shoebox stuff 
import tempfile 
from db_app import DropboxClient
from gd_app import GDriveClient
from otp import OneTimePad

# create the application
# TODO: move imports to __init__.py
app = Flask(__name__)

parse = ConfigParser.ConfigParser()
parse.read("config/app.ini")
app.config.update(dict(
    DATABASE    = os.path.join(app.root_path, parse.get("flask", "database")),
    SECRET_KEY  = parse.get("flask", "secret_key"),
    USERNAME    = parse.get("flask", "username"),
    PASSWORD    = parse.get("flask", "password")
))


########################################
# 
# DATABASE HELPERS
# 
########################################

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from users where user_id = ?', [session['user_id']], one=True)

def get_user_id(email):
    """Convenience method to look up the id for a email."""
    rv = query_db('select user_id from users where email = ?', [email], one=True)
    return rv[0] if rv else None

def get_files_for_user(user_id): 
    """Helper method to look up a user's files"""
    rv = query_db('select files from files where user_id = ?', [user_id], one=True)
    return rv[0] if rv else None

def create_user_files(user_id, file_obj):
    db = get_db()
    db.execute('insert into files (user_id, files) values (?, ?)', (user_id, file_obj))
    db.commit()

def update_user_files(user_id, file_obj):
    rv = query_db('update files set files = ? where user_id = ?', [file_obj, user_id], one=True)
    return rv[0] if rv else None

def build_json_file_object(file_name, cloud1, cloud2): 
    file_object = {'filename': file_name, 'cloud1': cloud1, 'cloud2': cloud2 }
    return json.dumps(file_object)
    #return '{"filename": "%s", "cloud1": "%s", "cloud2": "%s"}' % (file_name, cloud1, cloud2)


########################################
# 
# TODO: move to separate views.py file
# BEGIN ROUTES HERE
# 
########################################

@app.route('/')
def homepage():
    if g.user:
        return redirect(url_for('list'))
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return "YOU'RE LOGGED IN BRAHHHH"
        #return redirect(url_for('homepage'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from users where email = ?''', [request.form['email']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['password'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('homepage'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return "YOU'RE ALREADY LOGGED IN MATE"
        #return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        else:

            # insert the user into the users table
            db = get_db()
            db.execute('''insert into users (email, password) values (?, ?)''',
                    [request.form['email'], generate_password_hash(request.form['password'])])
            db.commit()

            # insert an empty record into the files table
            #db = get_db()
            #db.execute('''insert into files (user_id, files) values (?, ?)''',
                    #[get_user_id(request.form['email']), '[]'])
            #db.commit()

            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    session.pop('google_creds', None)
    session.pop('dropbox_access_token', None)
    return redirect(url_for('homepage'))


#if google_creds is not set AND if dropbox_access_token is not set,
#connect to google drive!
@app.route('/connect')
def connect():
    return render_template('connect.html', google=is_google_connected(), dropbox=is_dropbox_connected())

@app.route('/list')
def list(): 
    files = ''
    if is_dropbox_connected(): 
        db = DropboxClient(session['dropbox_access_token'])
        files = db.ls()
    return render_template('list.html', files=files, google=is_google_connected(), dropbox=is_dropbox_connected())

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_google_connected() or not is_dropbox_connected(): 
        flash("Connect your clouds before uploading!")
        return redirect(url_for('connect'))

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:

            # write uploaded file contents to temp file 
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(file.read())
                temp.flush()
                sbox_upload(temp, file.filename)
                temp.close()

            """
            # TODO: save session user id somewhere for easy access? _user_id?
            user_files      = get_files_for_user(session['user_id'])
            user_file_obj   = build_json_file_object(file.filename, 'dropbox', 'drive')
            if not user_files or user_files == '{}':
                print "user: "
                print session['user_id']
                print "adding new entry"
                print user_files

                print "printing new file obj "
                print user_file_obj

                json_str = []
                json_str.append(user_file_obj)
                print "adding json string"
                print json_str
                create_user_files(session['user_id'], json.dumps(json_str))
            else: 
                print user_files
                print "you already got some files bro"
                user_files.append(user_file_obj)
                update_user_files(session['user_id'], json.dumps(user_files))

            print "user file object: \n"
            print json.loads(user_file_obj)

            # TODO: REMOVE HARDCODE
            new_file_obj = build_json_file_object(file.filename, 'dropbox', 'drive')
            print "new file object"
            print new_file_obj

            user_file_obj.append(new_file_obj)
            print "final file objecdt"
            print user_file_obj
            """

            #return "FILE SUCCESSFULLY UPLOADED!"
            #update_user_files(session['user_id'], user_file_obj)
            flash("File sucessfully uploaded!")
            return redirect(url_for('list'))
    return render_template('upload.html')

def sbox_upload(temp_fd, file_name): 
    """ Upload a file to Shoebox 

        This function calls the generate_padfile function in the otp class to
        generate a one time pad with the same length as the plaintext file. 
        It then encrypts the plaintext using the pad to create the ciphertext. 
        
        The key is then pushed to Dropbox, while the ciphertext is pushed
        to Google Drive. All intermediate data is stored as named temporary files,
        which are automatically deleted on close. 
    """

    # TODO: when uploading, hash the file names to something different 
    db = DropboxClient(session['dropbox_access_token'])
    gd = GDriveClient(session['google_creds'])
    otp = OneTimePad()

    """ hashing stuff 
    db_hash_obj = sha256(b"dropbox-" + file_name)
    db_name_hash = db_hash_obj.hexdigest()

    gd_hash_obj = sha256(b"gdrive-" + file_name)
    gd_name_hash = gd_hash_obj.hexdigest()

    db.put(temp_key.name, db_name_hash)
    db.put(temp_key.name, db_name_hash)
    """

    temp_key, temp_ct = otp.encrypt(temp_fd)
    db.put(temp_key.name, file_name)
    gd.put(temp_ct.name, file_name)

    temp_key.close()
    temp_ct.close()


""" instead of downloading, why don't we just let them view the file? """
@app.route('/file-viewer/<filename>')
def file_viewer(filename): 
    """
    get a fd to the conents of the file from cloud 1 
    get a fd to conents of file from cloud 2 

    pass them to otp.decrypt()
    get the decrypted contents of the file 
    pass that to a temporary viewer page 
    """
    #contents = sbox_download(filename)
    contents = "this is the contents of my file"
    return render_template("file-viewer.html", filename=filename, contents=contents)

def sbox_download(file_name):
    db = DropboxClient(session['dropbox_access_token'])
    gd = GDriveClient(session['google_creds'])
    otp = OneTimePad()

    temp_key = db.get(file_name)
    temp_ct = gd.get(file_name)
    temp_pt = otp.decrypt(temp_key, temp_ct)

    contents = temp_pt.read()

    temp_key.close()
    temp_ct.close()
    temp_pt.close()
    return contents

########################################
# 
# TEMP DEBUGGING ROUTES
# 
########################################

@app.route('/debug')
def dump():
    if 'google_creds' in session and 'dropbox_access_token' in session:
        return "you got that good stuff"
    if 'google_creds' in session:
        return "only google"
    if 'dropbox_access_token' in session: 
        return "only dropbox"
    return "nothing bro"

@app.route('/delete-files')
def delete(): 
    query_db("delete from files where user_id = ?", [session['user_id']], one=True)
    return "deleted files!"

@app.route('/test')
def test(): 
    db = DropboxClient(session['dropbox_access_token'])
    fd = db.get('test_file.txt')
    if fd: 
        return fd.read()
    else: 
        return "nah nothing bro"
    #user_file_obj = get_files_for_user(session['user_id'])
    #print "printing user file obj"
    #print user_file_obj
    #if not user_file_obj or user_file_obj == '{}':
        #print "user: "
        #print session['user_id']
        #print "no files for you!"
    #else: 
        #print "you got files"
        #print json.loads(user_file_obj)


########################################
# 
# GOOGLE OAUTH ROUTES
# 
########################################

@app.route('/google')
def google():
  if 'google_creds' not in session:
    return redirect(url_for('oauth2callback'))

  credentials = client.OAuth2Credentials.from_json(session['google_creds'])
  if credentials.access_token_expired:
    return redirect(url_for('oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v2', http_auth)
    files = drive_service.files().list().execute()
    return redirect(url_for('connect'))
    #return "PRINTING FILES HERE"
    #return json.dumps(files)
    

@app.route('/google/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'config/client_secrets.json',
      scope='https://www.googleapis.com/auth/drive.file',
      redirect_uri=url_for('oauth2callback', _external=True))
  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)
  else:
    auth_code = request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    session['google_creds'] = credentials.to_json()
    return redirect(url_for('google'))

def is_google_connected(): 
    return True if 'google_creds' in session else False


########################################
# 
# DROPBOX OAUTH ROUTES
# 
########################################

# TODO: move to config!
def get_dropbox_auth_flow():
    redirect_uri = url_for('dropbox_auth_finish', _external=True)
    dropbox_key     = parse.get("creds", "dropbox.app_key")
    dropbox_secret  = parse.get("creds", "dropbox.app_secret")
    return DropboxOAuth2Flow(dropbox_key, dropbox_secret, redirect_uri, session, "dropbox-auth-csrf-token")

# URL handler for /dropbox-auth-start
@app.route('/dropbox')
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow().start()
    return redirect(authorize_url)

# URL handler for /dropbox-auth-finish
@app.route('/dropbox/dropbox-auth-finish')
def dropbox_auth_finish():
    try:
        access_token, user_id, url_state = get_dropbox_auth_flow().finish(request.args)
    except:
        abort(400)
    else:
        session['dropbox_access_token'] = access_token
    return redirect(url_for('connect'))

def is_dropbox_connected(): 
    return True if 'dropbox_access_token' in session else False
