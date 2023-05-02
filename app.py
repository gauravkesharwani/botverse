import logging
import Chatter
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)
# A very simple Flask Hello World app for you to get started with...

# Setup the secret key and the environment
app.config.update(SECRET_KEY='osd(99092=36&462134kjKDhuIS_d23', ENV='development')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=4)

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'

)

logger = logging.getLogger(__name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.name


@app.before_request
def check_session():
    if "login_time" not in session:
        session["login_time"] = str(datetime.now())


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/?ref=<referrer>")
# def refer():
#     return render_template("index.html")


@app.route("/about-us")
def about():
    return render_template("about.html")


@app.route("/modal")
def modal():
    return render_template("ui-modals.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/projects-grid')
    return render_template("login.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect('/login')

    return render_template("signup.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/privacy-policy")
def privacy():
    return render_template("privacy-policy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/projects-grid")
def grid():
    return render_template("projects-grid.html")


@app.route("/apps")
def apps():
    return render_template("apps.html")


@app.route("/apps-marketing-seo")
def apps_seo():
    return render_template("apps-marketing-seo.html")


@app.route("/apps-productivity")
def apps_productivity():
    return render_template("apps-productivity.html")


@app.route("/apps-chatbot")
def apps_chatbot():
    return render_template("apps-chatbot.html")


@app.route("/apps-copywriting")
def apps_copywriting():
    return render_template("apps-copywriting.html")


@app.route("/apps-hr-recruiting")
def apps_hr_recruiting():
    return render_template("apps-hr-recruiting.html")


@app.route("/apps-product-dev")
def apps_product_dev():
    return render_template("apps-product-dev.html")


@app.route("/apps-spreadsheets")
def apps_spreadsheets():
    return render_template("apps-spreadsheets.html")


@app.route("/apps-learning")
def apps_learning():
    return render_template("apps-learning.html")


@app.route("/projects-overview")
def overview():
    return render_template("projects-overview.html")


@app.route("/blogs")
def blogs():
    return render_template("blogs.html")


@app.route("/blog-1")
def blog1():
    return render_template("blog-1.html")


@app.route("/blog-2")
def blog2():
    return render_template("blog-2.html")


@app.route("/projects-create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        return redirect('/projects-overview')
    return render_template("projects-create.html")


@app.route("/chat")
def get_bot_response():
    userText = request.args.get('msg')
    logger.debug("Conversation Customer:" + userText)

    response = Chatter.get_response(userText)
    logger.debug("Conversation Chatbot: " + response)

    return response


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        if not name or not email:
            return render_template('404-error.html', message='Name and email are required.')
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            print(existing_user)
            return redirect(url_for('success', user_id=existing_user.id))

        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('success', user_id=user.id))
    return render_template('form.html')


@app.route('/success/<int:user_id>')
def success(user_id):
    user = User.query.get(user_id)
    if user:
        user.id = 212 + user.id
        return render_template('success.html', user=user)
    return render_template('404-error.html', message='User not found.')


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
