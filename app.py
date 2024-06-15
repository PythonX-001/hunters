from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import Flask, request, render_template
import os
import html
import bs4
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    username = session.get('username', None)
    return render_template('index.html', username=username)
@app.route('/bountylist')
@login_required

def bountylist():
    return render_template('hunted.html')

@app.route('/addbounty')
@login_required

def addbounty():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login_user():  # Renamed from 'login' to 'login_user'
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    session['username'] = username
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    # Emit 'leave' event before logging out
    socketio.emit('leave', {'username': session.get('username')}, room='main_room')
    session.pop('username', None)
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('loginPage'))

@app.route('/loginPage')
def loginPage():
    return render_template('login.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = 'main_room'
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = 'main_room'
    leave_room(room)
    send(username + ' has left the room.', room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = 'main_room'
    color = "#" + format(hash(username) % 0xFFFFFF, '06X')  # Generate a unique color based on username
    send({'username': username, 'message': message, 'color': color}, room=room)


from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
import html
import bs4
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    username = session.get('username', None)
    return render_template('index.html', username=username)

@app.route('/bountylist')
@login_required
def bountylist():
    return render_template('hunted.html')

@app.route('/addbounty')
@login_required
def addbounty():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login_user():  # Renamed from 'login' to 'login_user'
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    session['username'] = username
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    # Emit 'leave' event before logging out
    socketio.emit('leave', {'username': session.get('username')}, room='main_room')
    session.pop('username', None)
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('loginPage'))

@app.route('/loginPage')
def loginPage():
    return render_template('login.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = 'main_room'
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = 'main_room'
    leave_room(room)
    send(username + ' has left the room.', room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = 'main_room'
    color = "#" + format(hash(username) % 0xFFFFFF, '06X')  # Generate a unique color based on username
    send({'username': username, 'message': message, 'color': color}, room=room)

@app.route("/submitimg", methods=["POST"])
def submit():
    try:
        # Save the uploaded image file
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving image to: {image_path}")  # Debugging statement
            image_file.save(image_path)
            image_url = f"/static/uploads/{filename}"
        else:
            image_url = ""
            print("No image file provided.")  # Debugging statement

        name = str(request.form.get("name"))
        price = str(request.form.get("price"))  # Make sure to get the price
        stars = int(request.form.get("stars"))

        # Generate the star icons based on the rating
        star_icons = '<i class="fa-solid fa-skull" style="color: #e12d2d;"></i>' * stars

        html_code = '''
        <div class="card">
            <img class="image-sec" src="{}" alt="">
            <div class="details">
                <div><div class="name">{}</div>
                <div class="stars">{}</div></div>
                <div class="price">${}</div>
            </div>
        </div>
        '''
        html_code = html_code.format(image_url, name, star_icons, price)
        soup = bs4.BeautifulSoup(html_code, "html.parser")

        updated_html_code = str(soup)

        # Open a file called "hunted.html" and add the updated HTML code to the div id="elementsinput"
        with open("templates/hunted.html", "r") as f:
            html_file = f.read()

        soup = bs4.BeautifulSoup(html_file, "html.parser")

        elementsinput_div = soup.find("div", id="elementsinput")
        elementsinput_div.insert(1, html.unescape(updated_html_code))

        with open("templates/hunted.html", "w") as f:
            f.write(str(soup))
        with open("templates/hunted.html", "r") as f:
            html_code = f.read()

        # Replace all HTML entities in the HTML code
        updated_html_code = html_code.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        # Write the updated HTML code to the file
        with open("templates/hunted.html", "w") as f:
            f.write(updated_html_code)

        return render_template("hunted.html")

    except KeyError as e:
        flash(f"Missing data: {str(e)}", "error")
        return redirect(url_for('addbounty'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('addbounty'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)