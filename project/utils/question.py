import project
from project.database import query_db, execute_db

question_types = {"multiple choice": 1, "short answer": 2}#, "essay": 3}
question_ints  = {question_types[i]: i for i in question_types}

def get_question(qid):
    result = query_db("SELECT * FROM questions WHERE qid=?", (qid,), True)
    t = result["type"]
    result["type"] = (t, question_ints[t])
    return result

def search_question(term):
    term = "%" + term + "%"
    result = query_db("SELECT * FROM questions WHERE text LIKE ?", (term,))
    return result

def create_question(text, qtype, answer_choices, answer):
    execute_db("INSERT INTO questions (text, type, answer_choices, answer) VALUES (?, ?, ?, ?)",
               (text, qtype, answer_choices, answer))

def edit_question(qid, text, qtype, answer_choices, answer):
    execute_db("UPDATE questions SET text=?, type=?, answer_choices=?, answer=?\
                WHERE qid=?", (text, qtype, answer_choices, answer, qid))

def attach_to_assessment(qid, aid):
    execute_db("INSERT INTO question_map VALUES (?, ?)", (qid, aid))

def detach_from_assessment(qid, aid):
    execute_db("DELETE FROM question_map WHERE qid=? AND aid=?", (qid, aid))

def assessment_has_question(qid, aid):
    r = query_db("SELECT count(*) AS c FROM question_map WHERE qid=? AND aid=?",
                 (qid, aid), True)["c"]
    return r > 0

def delete_question(qid):
    execute_db("DELETE FROM question_map WHERE qid=?", (qid,))
    execute_db("DELETE FROM questions WHERE qid=?", (qid,))

def questions_in_assessment(aid):
    return query_db("SELECT * FROM questions WHERE qid IN (SELECT qid FROM question_map WHERE aid=?)", (aid,))

def save_question_response(uid, aid, qid, text):
    execute_db("DELETE FROM student_answers WHERE uid=? AND aid=? AND qid=?",
               (uid, aid, qid))
    execute_db("INSERT INTO student_answers (uid, aid, qid, response) VALUES (?, ?, ?, ?)",
               (uid, aid, qid, text))

def get_question_response(uid, aid, qid):
    res = query_db("SELECT response FROM student_answers WHERE uid=? AND aid=? AND qid=?",
                   (uid, aid, qid), True)
    if res is None:
        return None
    return res["response"]

@project.app.context_processor
def inject_funcs():
    return {"has_question": assessment_has_question}
