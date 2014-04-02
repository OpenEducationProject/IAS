from project import app
from project.views import *

def add_url_routes(routes_tuple):
    for route, view_function in routes_tuple:
        app.add_url_rule(route, view_func=view_function, methods=["GET", "POST"])

add_url_routes((
    ('/', core.index),
    ('/login/', authentication.login),
    ('/logout/', authentication.logout),
    ('/assessment/', assessments.show_assessments),
    ('/assessment/new/', assessments.make_assessment),
    ('/assessment/<int:aid>/delete/', assessments.delete_assessment_view),
    ('/assessment/<int:aid>/edit/', assessments.edit_assessment_properties),
    ('/assessment/<int:aid>/enable/', assessments.enable_assessment_view),
    ('/assessment/<int:aid>/disable/', assessments.disable_assessment_view),
    ('/assessment/<int:aid>/select/', assessments.select_assessment),
    ('/assessment/<int:aid>/questions/', assessments.assessment_questions),
    ('/assessment/<int:aid>/take/', assessments.take_assessment),
    ('/assessment/<int:aid>/take/question/<int:qid>/', assessments.assessment_question),
    ('/assessment/<int:aid>/take/question/<int:qid>/save/', assessments.assessment_answer_save),
    ('/assessment/<int:aid>/analytics/', assessments.assessment_analytics),
    ('/assessment/unselect/', assessments.unselect_assessment),
    ('/question/', questions.question_dashboard),
    ('/question/new/', questions.make_question),
    ('/question/search/', questions.search_question_view),
    ('/question/<int:qid>/attach/', questions.add_to_assessment),
    ('/question/<int:qid>/detach/', questions.rm_from_assessment),
    ('/question/<int:qid>/delete/', questions.delete_question_view),
    ('/question/<int:qid>/edit/', questions.edit_question_view),
    ('/question/<int:qid>/preview/', questions.preview_question),
))
