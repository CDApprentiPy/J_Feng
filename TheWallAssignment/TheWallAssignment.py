from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
import os, binascii
from datetime import datetime
import logging

# For checking to see if a given email is in a valid format.
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app, 'thewall_assignment')
app.secret_key = "secret"

# Can delete once wall is done. Shows all the database.
def success():
    flash("SUCCESS!")
    query = "SELECT * FROM users JOIN messages ON users.id = messages.user_id JOIN comments ON users.id = comments.user_id"
    users = mysql.query_db(query)
    return users

@app.route("/")
def home():
    return render_template("index.html")

# To delete after assignment is done.
@app.route("/wall")
def wall():
    return render_template("wall.html")

@app.route("/register", methods=["POST"])
def register():
    # If the form is not filled out.
    if len(request.form['first_name']) < 1 and len(request.form['last_name']) < 1 and len(request.form['email']) < 1 and len(request.form['password']) < 1 and len(request.form['confirm_password']) < 1:
        flash("Please fill out the form.")
        return redirect("/")

    # Validates the name.
    if len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
        flash("Name must be more than 2 characters long.")
        name = False
    elif not request.form['first_name'].isalpha() or not request.form['last_name'].isalpha():
        flash("Name must only contain letters.")
        name = False
    else:
        session["first_name"] = request.form["first_name"]
        session["last_name"] = request.form["last_name"]
        name = True

    # Validates the email.
    if len(request.form['email']) < 1:
        flash("Email must not be blank.")
        email = False
    elif not email_regex.match(request.form['email']):
        flash("Invalid email address.")
        email = False
    else:
        session["email"] = request.form["email"]
        email = True

    # Validates the password.
    if len(request.form['password']) < 8:
        flash("Password must be more than 8 characters.")
        password = False
    elif request.form['password'] != request.form['confirm_password']:
        flash("Passwords must match.")
        password = False
    else:
        password = True

    # Validates which fields are complete, and saves the field, while reseting the incomplete fields.
    if name == True and email == False and password == False:
        return render_template("index.html", first_name=session["first_name"], last_name=session["last_name"])
    elif name == False and email == True and password == False:
        return render_template("index.html", email=session["email"])
    elif name == False and email == False and password == True:
        return render_template("index.html")
    elif name == True and email == True and password == False:
        return render_template("index.html", first_name=session["first_name"], last_name=session["last_name"], email=session["email"])
    elif name == True and email == False and password == True:
        return render_template("index.html", first_name=session["first_name"], last_name=session["last_name"])
    elif name == False and email == True and password == True:
        return render_template("index.html", email=session["email"])
    elif name == False and email == False and password == False:
        return render_template("index.html")
    # If form is complete, it will create a hashed password, and insert the registration info to the database.
    else:
        query = "SELECT email FROM users"
        queries = mysql.query_db(query)
        # Checks to see if the email inputted is already in the database.
        for q in range(0, len(queries)):
            for key in queries[q]:
                print queries[q][key]
                print session["email"]
                if queries[q][key] == session["email"]:
                    flash("That email is already registered.")
                    return redirect("/")
        # If it's a new registration, this will hash the password.
        salt = binascii.b2a_hex(os.urandom(10))
        hashed_pw = md5.new(request.form['password'] + salt).hexdigest()
        # Insert the user inputs into the database as a new user.
        query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at) VALUES (:first_name, :last_name, :email, :hashed_pw, :salt, NOW())"

        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'hashed_pw': hashed_pw,
            'salt': salt
        }

        mysql.query_db(query, data)

        return redirect("/logged_in")

@app.route("/login", methods=["POST"])
def login():
    session["l_email"] = request.form["l_email"]
    session["l_password"] = request.form["l_password"]

    # Pulls user's info from the database by comparing the email.
    query = "SELECT * FROM users WHERE users.email = '{}'".format (session["l_email"])
    queries = mysql.query_db(query)
    if queries == []:
        flash("This email is not registered.")
        return redirect("/")

    # Compares the password inputted (and hashed) with the hashed password in the database.
    for q in range(0, len(queries)):
        for key in queries[q]:
            if key == "password":
                hashed_pw = queries[q][key]
            if key == "salt":
                salt = queries[q][key]
            if key == "first_name":
                session["first_name"] = queries[q][key]
            if key == "last_name":
                session["last_name"] = queries[q][key]
            if key == "id":
                session["id"] = queries[q][key]

        unhashed_pw = md5.new(session["l_password"] + salt).hexdigest()

        if unhashed_pw == hashed_pw:
            return redirect("/logged_in")
        else:
            flash("Invalid password.")
            return redirect("/")

@app.route("/logged_in")
def logged_in():
    users = success()
    print users
    for q in range(0, len(users)):
        print q
        print users[q]

    return render_template("wall.html", all_users=users, first_name=session["first_name"])

@app.route("/post_message", methods=["POST"])
def post_message():
    query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(), :user_id)"

    data = {
        'message': request.form["text_post"],
        'user_id': session["id"]
    }

    post = mysql.query_db(query, data)

    for p in range(0, len(post)):
        print p

    date_posted = datetime.now()

    render_template("wall.html", all_posts=post, first_name=session["first_name"], last_name=session["last_name"], timestamp=date_posted)

@app.route("/logout")
def logout():
    flash("You are logged out!")
    session.clear()
    return redirect("/")


app.run(debug=True)