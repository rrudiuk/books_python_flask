import os

from flask import Flask, Blueprint, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')

    user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone();

    if user:
        # Flash message
        flash("Such username already exists")
        return redirect(url_for('signup'))

    # Hash user's password to store in DB
    hashedPassword = generate_password_hash(request.form.get("password"), method="pbkdf2:sha256", salt_length=8)

    new_user = db.execute("INSERT INTO users (username, name, password) VALUES (:username, :name, :password)",
            {"username": username, "name": name, "password": hashedPassword})
    db.commit()

    session["user_name"] = username
    session["logged_in"] = True
    session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone();
    # code to validate and add user to database goes here
    return redirect(url_for('search'))

@app.route("/login'")
def login():
    return render_template("login.html")
# Handle login POSTed data
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone();

    if not user or not check_password_hash(user[3], password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
    # if the above check passes, then we know the user has the right credentials
    # login code goes here
    else:
        session["user_name"] = username
        session["logged_in"] = True
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone();
        return redirect(url_for('search'))

@app.route("/logout")
def logout():
    session["user_name"] = None
    session["logged_in"] = False
    session["user_id"] = None
    session.clear()
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    if session.get("logged_in"):
        return render_template("search.html", user_id=session["user_id"][0])
    else:
        return render_template("error.html", message="Please log in to access this page")

@app.route("/search", methods=["POST"])
def books():
    """Search a book"""
    
    # Create list to store search results
    books_list = []

    # Get form information.
    search = request.form.get("search")
    # Request books from DB according to the search query
    books_list = db.execute("SELECT * FROM books WHERE title = :search or author = :search or isnb = :search", 
        {"search": search}).fetchall()
    # If nothing was found show the relevant page
    if len(books_list) == 0:
        return render_template("nothing_found.html", message="Nothing was found according to your search request.")

    return render_template("search_results.html", books=books_list)

@app.route("/book/<int:book_id>", methods=["GET"])
def book(book_id):
    """Lists details about a single book."""

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book... :(")

    reviews = []

    reviews = db.execute("SELECT review, score, user_id FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    all_reviews = db.execute("SELECT * FROM reviews JOIN users ON (reviews.user_id = users.id) WHERE book_id = :book_id",
        {"book_id": book_id}).fetchall()

    if len(reviews) > 0:
        return render_template("book.html", book=book, reviews=all_reviews)
    else:
        return render_template("book.html", book=book)

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
    review_score = request.form.get('score')
    review_review = request.form.get('review')
    review_user = session["user_id"][0]
    review_book = book_id

    if len(db.execute("SELECT * FROM reviews WHERE user_id = :user_id", {"user_id": review_user}).fetchall()) > 0:
        return render_template("error.html", message="This user already posted a review")

    new_review = db.execute("INSERT INTO reviews (book_id, user_id, review, score) VALUES (:book_id, :user_id, :review, :score)",
        {"book_id": review_book, "user_id": review_user, "review": review_review, "score": review_score})
    db.commit()

    return redirect(url_for("book", book_id=book_id))

app.run()

#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1Td50qJu7i4R1575N2pA", "isbns": "0441172717%2C0141439602"})
    #print(res.json())
    #books = db.execute("SELECT * FROM books").fetchall()