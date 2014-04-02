from flask import render_template, redirect, url_for, request, flash, session
from project.utils.assessments import can_edit_assessment
from project.utils.groups import require_teacher
from project.utils.question import (
        question_types, question_ints, get_question, search_question, create_question,
        attach_to_assessment, detach_from_assessment, delete_question, edit_question)

@require_teacher
def question_dashboard():
    return render_template("question_dashboard.html")

@require_teacher
def make_question():
    if request.method == "GET":
        return render_template("create_question.html", types=question_types)
    text = request.form["text"]
    qtype = request.form["type"]
    answer_choices = request.form["answer_choices"]
    answer = request.form["answer"]
    create_question(text, qtype, answer_choices, answer)
    return redirect(url_for("question_dashboard"))

@require_teacher
def edit_question_view(qid):
    if request.method == "GET":
        data = get_question(qid)
        text = data["text"]
        qtype = data["type"]
        choices = data["answer_choices"]
        answer = data["answer"]
        session["redirect_url"] = request.headers["Referer"]
        return render_template("edit_question.html", text=text, qtype=qtype,
                               answer_choices=choices, answer=answer, qid=qid,
                               types=question_types)

    text = request.form["text"]
    qtype = request.form["type"]
    answer_choices = request.form["answer_choices"]
    answer = request.form["answer"]
    edit_question(qid, text, qtype, answer_choices, answer)
    return redirect(session["redirect_url"])

@require_teacher
def search_question_view():
    if request.method != "POST" and session["search_query"] == "":
        return redirect(url_for("question_dashboard"))
    if request.method == "POST":
        result = search_question(request.form["key"])
        session["search_query"] = request.form["key"]
    else:
        result = search_question(session["search_query"])
    if result == []:
        flash("No results found.", "warning")
    return render_template("question_search_result.html",
                           result=result,
                           types=question_ints)

@require_teacher
def add_to_assessment(qid):
    if session["selected_test"] == -1:
        flash("<strong>No test selected!</strong> Please select a test.", "danger")
        return redirect(url_for("show_assessments"))
    if not can_edit_assessment(session["uid"], session["selected_test"]):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    attach_to_assessment(qid, session["selected_test"])
    return redirect(url_for("search_question_view"))

@require_teacher
def rm_from_assessment(qid):
    if session["selected_test"] == -1:
        flash("<strong>No test selected!</strong> Please select a test.", "danger")
        return redirect(url_for("show_assessments"))
    if not can_edit_assessment(session["uid"], session["selected_test"]):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    detach_from_assessment(qid, session["selected_test"])
    return redirect(request.headers["Referer"])

@require_teacher
def delete_question_view(qid):
    delete_question(qid)
    return redirect(url_for("search_question_view"))

@require_teacher
def preview_question(qid):
    question = get_question(qid)
    question["answer_choices"] = question["answer_choices"].split(",")
    return render_template("question_preview.html", q=question, enumerate=enumerate,
                           previous=request.headers["Referer"])
