from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oh-so-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

@app.route("/")
def show_survey_choices_form():
    """Show form to select a survey"""

    return render_template("select_survey.html", surveys=surveys)

@app.route("/", methods=["POST"])
def select_survey():
    """Select a survey."""

    survey_id = request.form['survey_code']

    # don't let them re-take a survey until cookie times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already_completed.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_intro.html",
                           survey=survey)

@app.route('/start', methods=['POST'])
def start_survey():
    """Clear responses from session"""

    session[RESPONSES_KEY] = []

    return redirect('/questions/0')

@app.route('/questions/<int:quest_id>')
def display_question(quest_id):
    """Shows current survey question and lists choices as radio buttons"""
    
    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        return redirect('/')

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')

    if (len(responses) != quest_id):
        flash(f'{quest_id} is an invalid question id.')
        return redirect(f'/questions/{len(responses)}')

    question = survey.questions[quest_id]

    return render_template('survey_question.html', quest_num=quest_id, question=question)

@app.route('/answer', methods=['POST'])
def send_answer():
    """Save answer and redirect to next question"""

    selection = request.form['answer']
    text = request.form.get("text", "")

    #add selection to to the session responses list
    responses = session[RESPONSES_KEY]
    responses.append({"selection": selection, "text": text})

    # add response to session
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')

    else:
        return redirect(f'/questions/{len(responses)}')

@app.route('/complete')
def survey_complete():
    """Show thank you message and list responses"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("complete.html",
                           survey=survey,
                           responses=responses)

    # Set cookie showing this survey has already been completed and cannot be retaken
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response

    # return render_template('complete.html')
