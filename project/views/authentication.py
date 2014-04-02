from flask import flash, render_template, request, session, url_for, redirect
from project.utils.authentication import authenticate

def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = authenticate(username, password)
    if user is False:
        flash("<strong>Authentication failure.</strong> Please try again.",
              "danger")
        return render_template("login.html")

    session["username"] = user["username"]
    session["uid"] = user["uid"]
    session["selected_test"] = -1
    session["search_query"] = ""
    
    flash("<strong>Login successful.</strong>", "success")
    return redirect(url_for("index"))

def logout():
    session.pop("username", None)
    session.pop("uid", None)
    flash("<strong>Logout successful.</strong>", "success")
    return redirect(url_for("login"))
