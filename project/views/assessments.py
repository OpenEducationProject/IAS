from flask import render_template, redirect, url_for, flash, session, request
from project.utils.assessments import (
        can_take_assessment, can_view_assessment_answers, can_edit_assessment,
        can_create_assessment, create_assessment, get_assessments_for_group,
        available_assessments, assessment_info, delete_assessment, enable_assessment,
        disable_assessment, edit_assessment, grade_assessment, conclude_assessment,
        assessment_grades, students_taken)
from project.utils.authentication import require_login
from project.utils.groups import get_user_groups, require_teacher
from project.utils.question import (questions_in_assessment, question_ints,
                                    assessment_has_question, get_question,
                                    save_question_response, get_question_response)

@require_login
def show_assessments():
    assns = [assessment_info(i) for i in available_assessments(session["uid"])]
    assns = [i for i in assns if i is not None]
    return render_template("assessment_list.html", assessments=assns)

@require_teacher
def make_assessment():
    if request.method == "GET":
        return render_template("create_assessment.html",
                               groups=get_user_groups(session["uid"]))
    try:
        title = request.form["title"]
        description = request.form["description"]
        group_id = int(request.form["group"])
        time = int(request.form["time"]) * int(request.form["time-multiplier"])
        max_attempts = int(request.form["max_attempts"])
    except:
        flash("<strong>Assessment creation failed.</strong> Check your parameters.", "danger")
        return render_template("create_assessment.html", groups=get_user_groups(session["uid"]))
    if can_create_assessment(session["uid"], group_id):
        create_assessment(title, description, group_id, time, max_attempts)
        flash("<strong>Assessment created.</strong>", "success")
    else:
        flash("<strong>You may not create assessments for that class.</strong>", "danger")
    return redirect(url_for("show_assessments"))

@require_teacher
def edit_assessment_properties(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    session["selected_test"] = aid
    if request.method == "GET":
        return render_template("edit_assessment_properties.html", a=assessment_info(aid),
                               groups=get_user_groups(session["uid"]))
    title = request.form["title"]
    description = request.form["description"]
    group_id = int(request.form["group"])
    time = int(float(request.form["time"])) * int(request.form["time-multiplier"])
    max_attempts = int(request.form["max_attempts"])
    edit_assessment(aid, title, description, group_id, time, max_attempts)
    flash("<strong>Assessment edited.</strong>", "success")
    return redirect(url_for("show_assessments"))

@require_teacher
def delete_assessment_view(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    delete_assessment(aid)
    flash("<strong>Assessment deleted.</strong>", "success")
    return redirect(url_for("show_assessments"))

@require_teacher
def enable_assessment_view(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    enable_assessment(aid)
    flash("<strong>Assessment enabled.</strong>", "success")
    return redirect(url_for("show_assessments"))

@require_teacher
def disable_assessment_view(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You cannot edit this assessment.</strong>", "danger")
        return redirect(url_for("show_assessments"))
    disable_assessment(aid)
    flash("<strong>Assessment disabled.</strong>", "success")
    return redirect(url_for("show_assessments"))

@require_teacher
def select_assessment(aid):
    session["selected_test"] = aid
    return redirect(url_for("show_assessments"))

@require_teacher
def unselect_assessment():
    session["selected_test"] = -1
    return redirect(url_for("show_assessments"))

@require_teacher
def assessment_questions(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You may not edit questions on this assessment!</strong>", "danger")
        return redirect(url_for("show_assessments"))
    results = questions_in_assessment(aid)
    return render_template("assessment_questions.html", aid=aid, questions=results,
                           types=question_ints)

@require_teacher
def assessment_analytics(aid):
    if not can_edit_assessment(session["uid"], aid):
        flash("<strong>You may not view analytics for this assessment!</strong>", "danger")
        return redirect(url_for("show_assessments"))

    questions = questions_in_assessment(aid)
    num_question = len(questions)
    num_students = students_taken(aid)
    grades_all = assessment_grades(aid)
    grades_tuple = sorted(grades_all.items(), key=lambda x:-x[1])
    grades = grades_all.values()
    mean = float(sum(grades))/len(grades)
    median = float(sorted(grades)[len(grades)/2])

    return render_template("analytics_home.html", a=assessment_info(aid),
                           n_questions=num_question, n_students=num_students,
                           mean=mean, median=median, grades=grades_tuple)

@require_login
def take_assessment(aid):
    if not can_take_assessment(session["uid"], aid):
        flash("<strong>You cannot take this assessment!</strong>", "danger")
        return redirect(url_for("show_assessments"))
    questions = questions_in_assessment(aid)
    questions = [i["qid"] for i in questions]
    if len(questions) == 0:
        flash("<strong>There are no questions in this assessment.</strong> Please contact your teacher.", "danger")
        return redirect(url_for("show_assessments"))
    return redirect(url_for('assessment_question', aid=aid, qid=questions[0]))

@require_login
def assessment_question(aid, qid):
    if not can_take_assessment(session["uid"], aid):
        flash("<strong>You cannot take this assessment!</strong>", "danger")
        return redirect(url_for("show_assessments"))
    if not assessment_has_question(qid, aid):
        flash("<strong>Uh-oh!</strong> This assessment does not contain the question you requested.", "danger")
        return redirect(url_for("show_assessments"))
    questions = questions_in_assessment(aid)
    questions = [i["qid"] for i in questions]
    qthis = questions.index(qid)
    qprev = questions[qthis - 1] if qthis > 0 else None
    qnext = questions[qthis + 1] if qthis < (len(questions) - 1) else None
    print qprev, qnext
    question = get_question(qid)
    # comment next line out for funny bug
    question["answer_choices"] = question["answer_choices"].split(",")
    return render_template("show_assessment_question.html", q=question,
                           qp=qprev, qn=qnext, a=assessment_info(aid),
                           response=get_question_response(session["uid"], aid, qid),
                           enumerate=enumerate)

@require_login
def assessment_answer_save(aid, qid):
    if not can_take_assessment(session["uid"], aid):
        flash("<strong>Uh-oh!</strong> Something's wrong. Your answers were not saved. Please contact your teacher.", "danger")
        return redirect(url_for("show_assessments"))
    if "proposed_next" in request.form and request.form["proposed_next"] != "done":
        qnext = int(request.form["proposed_next"])
        if not assessment_has_question(qnext, aid):
            flash("<strong>Uh-oh!</strong> Something's wrong. Your answers were not saved. Please contact your teacher.", "danger")
            return redirect(url_for("show_assessments"))
        if "answer" not in request.form:
            return redirect(url_for("assessment_question", aid=aid, qid=qnext))
        save_question_response(session["uid"], aid, qid, request.form["answer"])
        return redirect(url_for("assessment_question", aid=aid, qid=qnext))
    else:
        save_question_response(session["uid"], aid, qid, request.form["answer"])
        flash("Congratulations! You have completed the assessment.", "success")
        info = grade_assessment(session["uid"], aid)
        conclude_assessment(session["uid"], aid, info)
        flash("Your grade: " + str(info[2]*100) + "%")
        return redirect(url_for("show_assessments"))
