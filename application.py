import os

from flask import Flask, Blueprint, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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

@app.route("/login'")
def login():
    return render_template("login.html")

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
        flash("Such username already exists")
        return redirect(url_for('signup'))

    new_user = db.execute("INSERT INTO users (username, name, password) VALUES (:username, :name, :password)",
            {"username": username, "name": name, "password": password})
    db.commit()
    # code to validate and add user to database goes here
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    return 'Logout'


@app.route("/search", methods=["POST"])
def search():
    #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1Td50qJu7i4R1575N2pA", "isbns": "0441172717%2C0141439602"})
    #print(res.json())
    #books = db.execute("SELECT * FROM books").fetchall()
    return render_template("search.html")

@app.route("/book", methods=["POST"])
def book():
    """Search a book"""
    
    # Create list to store search results
    books_list = []

    # Get form information.
    search = request.form.get("search")
    # Request books from DB according to the search query
    books_list = db.execute("SELECT title, author, year FROM books WHERE title = :search or author = :search or isnb = :search", {"search": search}).fetchall()
    # If nothing was found show the relevant page
    if len(books_list) == 0:
        return render_template("nothing_found.html", message="Nothing was found according to your search request.")

    return render_template("search_results.html", books=books_list)

#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1Td50qJu7i4R1575N2pA", "isbns": "0441172717%2C0141439602"})
    #print(res.json())
    #books = db.execute("SELECT * FROM books").fetchall()