from flask import Flask, render_template, redirect, request, session, flash
import re
import datetime

app = Flask(__name__)
app.secret_key = "secret"

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def root():
    today = datetime.date.today()
    todayDate = str(today.year) + "-" + str(today.month) + "-" + str(today.day)
    todayList = todayDate.split("-")
    session["maxday"] = todayList

    return render_template("index.html", maxday=session["max"])

@app.route("/process", methods=["POST"])
def process():
    if len(request.form["email"]) < 1 and len(request.form["fName"]) < 1 and len(request.form["lName"]) < 1 and len(request.form["bday"]) < 1 and len(request.form["pword"]) < 1 and len(request.form["confirm"]) < 1:
        flash("Please fill out the form.")
        return redirect("/")

    if len(request.form["email"]) < 1:
        flash("Email cannot be blank!")
        email = False
    elif not email_regex.match(request.form["email"]):
        flash("Invalid email address!")
        email = False
    else:
        session["email"] = request.form["email"]
        email = True

    if len(request.form["fName"]) < 1 or len(request.form["lName"]) < 1:
        flash("Name cannot be blank!")
        name = False
    elif not request.form["fName"].isalpha() or not request.form["lName"].isalpha():
        flash("Names must not contain numbers.")
        name = False
    else:
        session["fName"] = request.form["fName"]
        session["lName"] = request.form["lName"]
        name = True

    if len(request.form["pword"]) < 8:
        flash("Password must be more than 8 characters.")
        pword = False
    elif request.form["pword"].islower():
        flash("Password must contain at least 1 uppercase letter.")
        pword = False
    elif request.form["pword"].isalpha():
        flash("Password must contain at least one number.")
        pword = False
    elif request.form["pword"] != request.form["confirm"]:
        flash("Password and password confirmation must match.")
        pword = False
    else:
        session["pword"] = request.form["pword"]
        session["confirm"] = request.form["confirm"]
        pword = True

    if len(request.form["bday"]) < 1:
        flash("Must enter a birthdate.")
        bday = False
    elif request.form["bday"] != session["maxday"]:
        flash("Date must not be in the past.")
        bday = False
    else:
        session["bday"] = request.form["bday"]        
        bday = True

    if email == False and name == True and pword == True and bday == True:
        return render_template("index.html", fName=session["fName"], lName=session["lName"], pword=session["pword"], confirm=session["confirm"], bday=session["bday"])
    elif email == True and name == False and pword == True and bday == True:
        return render_template("index.html", email=session["email"], pword=session["pword"], confirm=session["confirm"], bday=session["bday"])
    elif email == True and name == True and pword == False and bday == True:
        return render_template("index.html", email=session["email"], fName=session["fName"], lName=session["lName"], bday=session["bday"])
    elif email == True and name == True and pword == True and bday == False:
        return render_template("index.html", email=session["email"], fName=session["fName"], lName=session["lName"], pword=session["pword"], confirm=session["confirm"])
    elif email == False and name == False and pword == True and bday == True:
        return render_template("index.html", pword=session["pword"], confirm=session["confirm"], bday=session["bday"])
    elif email == True and name == False and pword == False and bday == True:
        return render_template("index.html", email=session["email"], bday=session["bday"])
    elif email == True and name == True and pword == False and bday == False:
        return render_template("index.html", email=session["email"], fName=session["fName"], lName=session["lName"])
    elif email == False and name == True and pword == False and bday == True:
        return render_template("index.html", fName=session["fName"], lName=session["lName"], bday=session["bday"])

    elif email == False and name == True and pword == True and bday == False:
        return render_template("index.html", fName=session["fName"], lName=session["lName"], pword=session["pword"], confirm=session["confirm"])
    elif email == True and name == False and pword == False and bday == True:
        return render_template("index.html", email=session["email"], bday=session["bday"])
    elif email == True and name == False and pword == True and bday == False:
        return render_template("index.html", email=session["email"], pword=session["pword"], confirm=session["confirm"])
    elif email == False and name == False and pword == False and bday == True:
        return render_template("index.html", bday=session["bday"])
    elif email == False and name == True and pword == False and bday == False:
        return render_template("index.html", fName=session["fName"], lName=session["lName"])
    elif email == False and name == False and pword == True and bday == False:
        return render_template("index.html", pword=session["pword"], confirm=session["confirm"])
    elif email == True and name == False and pword == False and bday == False:
        return render_template("index.html", email=session["email"])
    else:
        return render_template("index.html", email=session["email"], fName=session["fName"], lName=session["lName"], pword=session["pword"], confirm=session["confirm"], bday=session["bday"])

app.run(debug=True)