from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, json, flash
import api
import util
import os, glob
from uuid import uuid4
from user import LoginForm, User
from flask_login import login_user, login_required, logout_user
from flask_login import LoginManager, current_user
import sys
from time import strftime, localtime
import datetime

TEST_LOG = __name__ + ' juanchen: '

this_function_name = sys._getframe().f_code.co_name

app = Flask(__name__)
app.secret_key = os.urandom(24)

# use login manager to manage session
login_manager = LoginManager()
# login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=app)


# The callback to reload User object.
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
@app.route('/home')
def home_page():
    print(this_function_name)

    surveys = api.get_all_general_surveys()
    is_signed_in = current_user.is_authenticated
    if is_signed_in:
        userid = api.get_user_id(current_user.username)
        if userid:
            return render_template('all_public_surveys.html', title="HOME", surveys=surveys, isSignedIn=is_signed_in, userid=userid)
    return render_template('all_public_surveys.html', title="HOME", surveys=surveys, isSignedIn=is_signed_in)


@app.route('/main')
@login_required
def main_page():
    userid = api.get_user_id(current_user.username)
    if userid:
        print(this_function_name)
        print('shit: '+userid)
        surveys = api.get_all_general_surveys()
        if surveys:
            return render_template('all_public_surveys.html', title="HOME", surveys=surveys, isSignedIn=True, userid=userid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(this_function_name)
    if request.method == 'POST':
        form = LoginForm()
        user_name = request.form.get('username', None)
        password = request.form.get('password', None)
        remember_me = request.form.get('remember_me', False)
        print(user_name, password, remember_me)
        user = User(user_name, password)
        if user.verify_password(password):
            login_user(user)
            return redirect(url_for('main_page'))
        else:
            flash("username and password do not match!")
            return render_template('signin.html', title="Sign In")
    return render_template('signin.html', title="Sign In")


@app.route('/register', methods=['GET', 'POST'])
def register():
    print(this_function_name)
    if request.method == 'GET':
        return render_template('register.html', title='Register Your Account')
    print('Log In')
    req_json = util.request_form_to_json(request)

    if req_json['action'] == 'getcode' and req_json['username'] != "":
        api.get_code(req_json['username'])
        warning = "Email Sent!"
        return render_template('register.html', title="Get Code", warning=warning)

    elif req_json['action'] == 'register':
        if req_json['code'] != "" and req_json['password'] != "" and req_json['username'] != "":
            res = api.register_user(req_json)
            if res:
                return render_template('register.html', title="Get Code", warning='Entered Wrong Code')

    warning = "Click Get Code first, Enter code from your email"
    return render_template('register.html', title="Get Code", warning=warning)


# get empty new survey form, restricted for signed in users '/users/id/surveys/'
# post: send filled form to spring backend server
@app.route('/surveys/', methods=['GET', 'POST'])
@login_required
def add_new_survey():
    print(this_function_name)
    if request.method == 'GET':
        print("GET Surveys")
        return render_template('newSurveyForm.html', title="Create Survey")

    survey_json = util.request_form_to_json(request)
    print(survey_json)
    if survey_json and survey_json['surveyType']:
        if survey_json['startTime'] == '':
            survey_json['startTime'] = strftime("%Y-%m-%d %H:%M", localtime())

        if survey_json['endTime'] == '':
            end_time = datetime.datetime.now() + datetime.timedelta(days=30)
            endTime = end_time.strftime("%Y-%m-%d %H:%M")
            survey_json['endTime'] = endTime
            rev = api.create_survey(survey_json)
            return redirect(url_for('get_survey_by_id', id=rev['id']))
    return render_template('newSurveyForm.html', title='CREATE SURVEY')


@app.route('/surveys/<sid>/addquestion', methods=['GET', 'POST'])
@login_required
def add_new_question(sid):
    '''
    GET: return selectQuestionType.html to let user choose question type
    POST: return createQuestion.html to let user create question content
    '''
    print(this_function_name)
    if request.method == 'GET':
        print("GET Questions")
        return render_template('selectQuestionType.html', title="New Question", surveyId=sid)
    survey_json = util.request_form_to_json(request)
    print(survey_json)
    question_type = survey_json['questionType']
    return render_template('createQuestion.html', title='New Question', surveyId=sid, questionType=question_type)


@app.route('/click_MySurveys', methods=['GET'])
@login_required
def click_MySurveys():
    userid = api.get_user_id(current_user.username)
    if userid:
        return redirect('/users/{0}/surveys'.format(userid))


@app.route('/surveys/<sid>/questions', methods=['POST'])
@login_required
def send_new_question(sid):
    '''
    Get question data and send to backend db
    '''
    print(this_function_name)
    question_json = util.request_form_to_json(request)
    print(question_json)
    rev_json = api.create_question(question_json)
    if rev_json is False:
        return "Add New Question Failed"
    survey = api.get_survey_by_id(int(sid))
    survey = util.extract_survey_json(survey)
    return render_template('surveydetail.html', title="Survey_Adding_Questions", survey=survey)


@app.route('/logout')
@login_required
def logout():
    print(this_function_name)
    logout_user()
    return redirect(url_for('login'))


@app.route('/surveys/<id>')
def get_survey_by_id(id):
    print(this_function_name)
    try:
        rev = api.get_survey_by_id(int(id))
        survey = util.extract_survey_json(rev)
        if survey:
            return render_template('surveydetail.html', title="Survey", survey=survey)
        else:
            return "Wrong Survey ID"
    except Exception:
        return "Wrong Survey ID"


@app.route('/users/<id>/surveys')
@login_required
def get_all_surveys_for_currentuser(id):
    # get_all_surveys_for_currentuser
    # under MySurveys Menu
    print(this_function_name)
    surveys = api.get_all_surveys_for_user(id)
    print(surveys)
    return render_template('mysurveys.html', surveys=surveys)

# TODO: publish survey, set end time ??
# TODO: REPORTing PAGE


###Invititations ###
@app.route('/surveys/<id>/invitations', methods=['POST'])
@login_required
def send_invitations(id):
    json = util.request_form_to_json(request)
    json['surveyId'] = id
    user_id = api.get_user_id(username=current_user.username)
    if user_id:
        json['userId'] = api.get_user_id(username=current_user.username)
        print(json)
        return api.send_invitations(json)


# ANSWER SURVEYS
@app.route('/surveys/<id>/answer')
def get_survey_form(id):
    rev = api.get_survey_by_id(int(id))
    survey = util.extract_survey_json(rev)
    is_signed_in = current_user.is_authenticated
    return render_template('answer_a_survey.html', title="Answer Survey", survey=survey, isSignedIn=is_signed_in)


# this should be the link send to users -> change the url send via emails
# get survey according to email link
@app.route('/private/surveys/<uuid>')
def get_survey_for_link(uuid):
    if uuid is not None:
        survey = api.get_survey_by_uuid(uuid)
        print(survey)
        survey = util.extract_survey_json(survey)
        survey['uuid'] = uuid
        print(survey)
        is_signed_in = current_user.is_authenticated
        if is_signed_in:
            userid = api.get_user_id(current_user.username)
            return render_template('answer_a_survey.html', title="Answer Survey", survey=survey, isSignedIn=is_signed_in, userid=userid)
    return render_template('answer_a_survey.html', title="Answer Survey", survey=survey, isSignedIn=is_signed_in)


# save answer via email link
@app.route('/private/surveys/<uuid>', methods=['POST'])
def save_answer_form_link(uuid):
    answer_json = util.request_form_to_json(request)
    answer_json['surveyLink'] = uuid
    answer = util.parse_answer_json(answer_json)
    rev = api.create_answer(answer)
    return str(rev)


@app.route('/surveys/<id>/answer', methods=['POST'])
def save_answer_form(id):
    '''
    :param id:
    :return:
    accept answer_a_survey page submission;
    '''
    answer_json = util.request_form_to_json(request)
    answer_json['surveyLink'] = api.get_survey_by_id(id)['link']
    answer = util.parse_answer_json(answer_json)
    rev = api.create_answer(answer)
    return str(rev)


# TODO: REPORT PAGE
# GET ANSWERS BY SURVEY_ID
@app.route('/click_MyReports', methods=['GET'])
@login_required
def click_MyReports():
    print(this_function_name)
    userid = api.get_user_id(current_user.username)
    if userid:
        return redirect('/users/{0}/reports'.format(userid))


@app.route('/users/<uid>/reports')
@login_required
def get_my_report_list(uid):
    # TODO: refine the report list to only show those matches
    surveys = api.get_all_surveys_for_user(uid)
    return render_template('my_report_list_page.html', uid=uid, title="ReportList", surveys=surveys)


@app.route('/users/<uid>/report/surveys/<sid>')
@login_required
def get_report(uid, sid):
    json = api.get_report_by_id(uid, sid)
    return "TBD"


# #Upload Images ###

@app.route("/surveys/<sid>/upload", methods=["POST"])
def upload(sid):
    """Handle the upload of a file."""
    question_json = util.request_form_to_json(request)
    if question_json['question'] == '':
        return "Pls input quesiton"
    print("=== Form Data ===")
    print(question_json)

    exact_path = os.path.join(os.getcwd(), "static/uploads")
    # try:
    #     os.makedirs(target)
    # except:
    #     return "Couldn't create upload directory: {}".format(target)
    images = []
    for f in request.files.getlist("file"):
        upload_key = str(uuid4())
        print(f)
        filename = f.filename.rsplit("/")[0]
        print (filename)
        newname = upload_key + '.' + filename.split('.')[-1]
        destination = "/".join([exact_path, newname])
        f.save(destination)
        images.append('static/uploads/'+ newname)

    if len(images) == 0:
        return "No Image uploaded!"
    question_json['questionContent'] = ';'.join(images)
    rev_json = api.create_question(question_json)
    if rev_json is False:
        return "Add New Question Failed"
    survey = api.get_survey_by_id(int(sid))
    survey = util.extract_survey_json(survey)
    return render_template('surveydetail.html', title="Survey_Adding_Questions", survey=survey)


# @app.route('/surveys/<sid>/questions', methods=['POST'])
# @login_required
# def send_new_question(sid):
#     '''
#     Get question data and send to backend db
#     '''
#     print(this_function_name)
#     question_json = util.request_form_to_json(request)
#     print(question_json)
#     rev_json = api.create_question(question_json)
#     if rev_json is False:
#         return "Add New Question Failed"
#     survey = api.get_survey_by_id(int(sid))
#     survey = util.extract_survey_json(survey)
#     return render_template('surveydetail.html', title="Survey_Adding_Questions", survey=survey)


@app.route("/files/<uuid>/<sid>")
def upload_complete(uuid, sid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = os.path.join(os.getcwd(), "static/uploads/{0}".format(uuid))
    # root = "/static/uploads/{}".format(uuid)
    print(root)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)
    return render_template("files.html", uuid=uuid, files=files, sid=sid )


if __name__ == '__main__':
    app.run(debug=True, port=12345)
