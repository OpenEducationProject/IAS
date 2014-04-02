import project
from project.database import query_db, execute_db
from project.utils.groups import (get_user_groups, current_user_in_group,
                                  get_users_in_group)
from project.utils.authentication import uid_to_realname
from project.utils.question import (questions_in_assessment, get_question_response)

"""
Assessments can have several "modes." Modes are integers describing how a
student can interact with the test:

    0: student cannot take the test, it is not available.
    1: student can take the test.
    2: student can view missed questions/answers, but not take the test.
"""

def used_attempts(uid, aid):
    attempts = query_db("SELECT attempt_num AS a FROM student_asm_info WHERE uid=? AND aid=?",
                        (uid, aid))
    attempts_already = [i["a"] for i in attempts]
    return max(attempts_already) if len(attempts_already) > 0 else 0

def conclude_assessment(uid, aid, grade):
    this_attempt = used_attempts(uid, aid) + 1
    execute_db("INSERT INTO student_asm_info (uid, aid, attempt_num) VALUES (?, ?, ?)",
               (uid, aid, this_attempt))
    execute_db("INSERT INTO student_score_cache (uid, aid, correct, attempt) VALUES (?, ?, ?, ?)",
               (uid, aid, grade[0], this_attempt))

def can_take_assessment(uid, aid):
    r = query_db(""" SELECT uid FROM users            WHERE uid IN
                    (SELECT uid FROM group_membership WHERE gid IN
                    (SELECT gid FROM assessments      WHERE aid=? AND mode=1))
                     AND uid=?""",
                 (aid, uid), True)
    attempts = used_attempts(uid, aid)
    max_attempts = query_db("SELECT max_attempts AS a FROM assessments WHERE aid=?",
                            (aid,), True)["a"]

    return r is not None and r["uid"] == uid and (attempts < max_attempts
                                                  or max_attempts == 0)

def can_view_assessment_answers(uid, aid):
    r = query_db(""" SELECT uid FROM users WHERE uid IN
                    (SELECT uid FROM group_membership WHERE gid IN
                    (SELECT gid FROM assessments WHERE aid=? AND mode=2))
                     AND uid=?""",
                 (aid, uid), True)
    return r is not None and r["uid"] == uid

def can_edit_assessment(uid, aid):
    gid = query_db("SELECT gid FROM assessments WHERE aid=?", (aid,), True)["gid"]
    ugroups = get_user_groups(uid)
    return gid in ugroups and (-2 in ugroups or -1 in ugroups)

def can_create_assessment(uid, gid):
    ugroups = get_user_groups(uid)
    return gid in ugroups and (-2 in ugroups or -1 in ugroups)

def create_assessment(title, description, group, time=3600, max_attempts=0):
    execute_db("""INSERT INTO assessments (title, description, gid, mode,
                                           time, max_attempts) VALUES
                                           (?, ?, ?, 0, ?, ?)""",
               (title, description, group, time, max_attempts))

def edit_assessment(aid, title, description, group, time, max_attempts):
    execute_db("""UPDATE assessments SET
                  title=?, description=?, gid=?, time=?, max_attempts=?
                  WHERE aid=?""",
               (title, description, group, time, max_attempts, aid))

def delete_assessment(aid):
    execute_db("DELETE FROM assessments WHERE aid=?", (aid,))

def enable_assessment(aid):
    execute_db("UPDATE assessments SET mode=1 WHERE aid=?", (aid,))

def disable_assessment(aid):
    execute_db("UPDATE assessments SET mode=0 WHERE aid=?", (aid,))

def get_assessments_for_group(gid):
    return [i["aid"] for i in query_db("SELECT aid FROM assessments WHERE gid=?", (gid,))]

def available_assessments(uid):
    assns = []
    for i in get_user_groups(uid):
        assns += get_assessments_for_group(i)
    return list(set(assns))

def assessment_info(aid):
    info = query_db("SELECT * FROM assessments WHERE aid=?", (aid,), True)
    if info is not None:
        info["time"] = int(float(info["time"]))
    return info

def grade_assessment(uid, aid):
    total = 0
    correct = 0
    for question in questions_in_assessment(aid):
        if question["type"] in [1, 2]:
            total += 1
            if question["answer"] == get_question_response(uid, aid, question["qid"]):
                correct += 1
    return (correct, total, float(correct)/total)

def assessment_grades(aid):
    results = query_db("SELECT * FROM student_score_cache WHERE aid=? ORDER BY attempt", (aid,))
    r = {}
    for result in results:
        r[result["uid"]] = result["correct"]
    return r

def students_taken(aid):
    res = query_db("SELECT count(*) AS count FROM student_score_cache WHERE aid=? AND attempt=1", (aid,), True)
    if res is None:
        return None
    return res["count"]

@project.app.context_processor
def inject_funcs():
    return {"assessment_info": assessment_info,
            "attempts_used": used_attempts}
