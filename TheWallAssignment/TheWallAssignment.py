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
# def success():
#     flash("SUCCESS!")
#     query = "SELECT users.id, users.first_name, users.last_name, users.email, users.password, users.salt, users.created_at, messages.message FROM users LEFT JOIN messages ON users.id = messages.user_id LEFT JOIN comments ON users.id = comments.user_id"
#     users = mysql.query_db(query)
#     return users

@app.route("/")
def home():
    return render_template("index.html")

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
        query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :hashed_pw, :salt, NOW(), NOW())"

        data = {
            'first_name': request.form['first_name'].capitalize(),
            'last_name': request.form['last_name'].capitalize(),
            'email': request.form['email'],
            'hashed_pw': hashed_pw,
            'salt': salt
        }

        mysql.query_db(query, data)

        return redirect("/logged_in")

@app.route("/login", methods=["POST"])
def login():
    session["email"] = request.form["l_email"]

    # Pulls user's info from the database by comparing the email.
    query = "SELECT * FROM users WHERE users.email = '{}'".format (session["email"])
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

        unhashed_pw = md5.new(request.form["l_password"] + salt).hexdigest()

        if unhashed_pw == hashed_pw:
            return redirect("/logged_in")
        else:
            flash("Invalid password.")
            return redirect("/")

@app.route("/logged_in")
def logged_in():
    query = "SELECT users.id, users.first_name, users.last_name, users.email, users.created_at, messages.message FROM users LEFT JOIN messages ON users.id = messages.user_id LEFT JOIN comments ON users.id = comments.user_id WHERE users.email = :email"

    data = {
        'email': session["email"]
    }

    logged_user = mysql.query_db(query, data)

    for user in range(0, len(logged_user)):
        for key in logged_user[user]:
            if key == "first_name":
                session["first_name"] = logged_user[user][key]
            if key == "last_name":
                session["last_name"] = logged_user[user][key]
            if key == "id":
                session["id"] = logged_user[user][key]

    return redirect("/wall")

# Displays the wall.
@app.route("/wall")
def wall():
    query = "SELECT messages.message, messages.created_at AS message_timestamp, users.first_name, users.last_name, messages.id AS message_id, messages.user_id FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
    posts = mysql.query_db(query)

    query = "SELECT comments.comment, comments.created_at AS comment_timestamp, users.first_name, users.last_name, comments.id AS comment_id, comments.message_id AS cmt_msg_id, comments.user_id AS user_id FROM comments LEFT JOIN users ON comments.user_id = users.id ORDER BY comments.created_at ASC"
    comments = mysql.query_db(query)

    return render_template("wall.html", all_posts=posts, all_comments=comments, first_name=session["first_name"], last_name=session["last_name"])

# When message is posted, this will insert the information into the database and save the user's id to the session.
@app.route("/post_message", methods=["POST"])
def post_message():
    text_post = request.form["text_post"]

    if len(text_post) == 0:
        flash("Please enter a message.")
        return redirect("/wall")
    else:
        query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(), :user_id)"

        data = {
            'message': request.form["text_post"],
            'user_id': session["id"]
        }

        mysql.query_db(query, data)

        return redirect("/wall")

# When user deletes their own message post, it will delete the message and the comments relating to that message from the database.
@app.route("/delete_post/<message_id>")
def delete_post(message_id):
    query = "DELETE FROM comments WHERE comments.message_id = :message_id" 
    
    query2 = "DELETE FROM messages WHERE messages.id = :message_id"

    data = {
        'message_id': message_id
    }

    mysql.query_db(query, data)
    mysql.query_db(query2, data)

    return redirect("/wall")

# When comment is posted, this will insert the information into the database and save the user's id to the session.
@app.route("/post_comment/<message_id>", methods=["POST"])
def post_comment(message_id):
    text_comment = request.form["text_comment"]

    if len(text_comment) == 0:
        flash("Please enter a comment.")
        return redirect("/wall")
    else:
        query = "INSERT INTO comments (comment, created_at, updated_at, message_id, user_id) VALUES (:comment, NOW(), NOW(), :message_id, :user_id)"

        data = {
            'comment': text_comment,
            'message_id': message_id,
            'user_id': session["id"]
        }

        mysql.query_db(query, data)

        return redirect("/wall")

# When user deletes their own comment, it will delete the information from the database.
@app.route("/delete_comment/<comment_id>")
def delete_comment(comment_id):
    query = "DELETE FROM comments WHERE comments.id = :comment_id" 
    
    data = {
        'comment_id': comment_id
    }

    mysql.query_db(query, data)

    return redirect("/wall")

# Logs user out, and clears sessions.
@app.route("/logout")
def logout():
    flash("You are logged out!")
    session.clear()
    return redirect("/")


app.run(debug=True)