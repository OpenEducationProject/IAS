from flask import session, flash, redirect, url_for
from functools import wraps
import project
from project.database import query_db, execute_db

def get_user_groups(uid):
    groups = query_db("SELECT gid FROM group_membership WHERE uid=?", (uid,))
    groups = [i["gid"] for i in groups]
    return groups

def get_users_in_group(gid):
    groups = query_db("SELECT uid FROM group_membership WHERE gid=?", (gid,))
    groups = [i["uid"] for i in groups]
    return groups

def user_in_group(uid, gid):
    return uid in get_users_in_group(gid)

def get_group_name(gid):
    return query_db("SELECT name FROM groups WHERE gid=?", (gid,), True)["name"]

def current_user_in_group(gid):
    return "uid" in session and user_in_group(session["uid"], gid)

def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user_in_group(-1):
            flash("You must be an administrator to access this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

def require_teacher(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not (current_user_in_group(-2) or current_user_in_group(-1)):
            flash("You must be a teacher to access this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

@project.app.context_processor
def inject_functions():
    return {"is_in_group": current_user_in_group,
            "group_name": get_group_name}
