from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oh-so-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

RESPONSES_KEY = 'responses'

@app.route('/')
def survey_intro():
    """Displays title of survey, the instructions, and a button to start the survey"""

    return render_template('survey_intro.html', survey=survey)

@app.route('/start', methods=['POST'])
def start_survey():
    session[RESPONSES_KEY] = []

    return redirect('/questions/0')

@app.route('/questions/<int:quest_id>')
def display_question(quest_id):
    """Shows current survey question and lists choices as radio buttons"""
    responses = session.get(RESPONSES_KEY)

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

    #get the user's selection
    selection = request.form['answer']

    #add selection to to the session responses
    responses = session[RESPONSES_KEY]
    responses.append(selection)
    session[RESPONSES_KEY] = responses

    print(session)

    if (len(responses) == len(survey.questions)):
        return redirect('/complete')

    else:
        return redirect(f'/questions/{len(responses)}')

@app.route('/complete')
def survey_complete():

    return render_template('complete.html')
