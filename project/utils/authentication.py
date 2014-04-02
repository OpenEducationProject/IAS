from flask import session, redirect, url_for, flash
from functools import wraps
import project
from project.database import query_db, execute_db
from hashlib import sha512

def account_exists(username):
    user = query_db("SELECT * FROM users WHERE username=?", [username], True)
    return user is not None

def authenticate(username, password):
    hashed = sha512(password).hexdigest()
    user = query_db("SELECT * FROM users WHERE username=? AND password=?",
                    (username, hashed), True)
    return user if user is not None else False

def create_account(username, password):
    if account_exists(username):
        return False
    hashed = sha512(password).hexdigest()
    execute_db("INSERT INTO USERS (username, password) VALUES (?, ?)",
               (username, hashed))
    return True

def username_to_uid(username):
    result = query_db("SELECT uid FROM users WHERE username=?", [username], True)
    return None if result is None else int(result["uid"])

def uid_to_username(uid):
    result = query_db("SELECT username FROM users WHERE uid=?", [uid], True)
    return None if result is None else result["username"]

def uid_to_realname(uid):
    result = query_db("SELECT fname, lname FROM users WHERE uid=?", [uid], True)
    return None if result is None else " ".join((result["fname"], result["lname"]))

def require_login(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "uid" not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

@project.app.context_processor
def inject_template_funcs():
    return {"usernameof": uid_to_username, "nameof": uid_to_realname}
