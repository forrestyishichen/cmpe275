
import requests
import util
from flask_login import current_user
import inspect

TEST_LOG = __name__ + '.py'

ERROR_LOG = __name__ + '.py ' + 'ERROR: '

SPRING_URL = 'http://ec2-35-174-138-128.compute-1.amazonaws.com:8080/'

cur_survey_id = None


def test_log(func, text=''):
    print('In {0} func: {1}, msg: {2}'.format(TEST_LOG, func, text))


def error_log(func, err=''):
    print('In {0} func: {1}, msg: {2}'.format(ERROR_LOG, func, err))


def get_code(email):
    try:
        url = SPRING_URL+'email_verify?email='+email
        test_log(inspect.stack()[0][3], url)
        rev = requests.get(SPRING_URL+'email_verify?email='+email)
        print(TEST_LOG + str(rev.status_code))
        if rev.status_code == 200:
            return True
        print(ERROR_LOG + 'Get Code Error')
        print(TEST_LOG + rev.text)
        return False
    except Exception as e:
        print(ERROR_LOG + 'Exception: Get Code Error')
        print(e)
        return False


def register_user(data):
    try:
        email = data['username']
        code = data['code']
        password = data['password']
        url = SPRING_URL+'signup?email='+email+'&code='+code+'&password='+password
        test_log(inspect.stack()[0][3], url)
        rev = requests.post(url)
        if rev.status_code == 200:
            return True
        error_log(inspect.stack()[0][3], 'register failed')
        error_log(inspect.stack()[0][3], 'rev.text')
        return False
    except Exception as e:
        print(e)
        error_log(inspect.stack()[0][3], "Exception: register failed")
        return False


def get_user_id(username):
    try:
        rev = requests.get(SPRING_URL + 'api/get_user_id?email=' + username)
        json = util.string_to_json(rev.text)
        print(json)
        return str(json['id'])
    except Exception as e:
        print (e)
        error_log(inspect.stack()[0][3], "get user id failed")
        return None


def get_username(user_id):
    try:
        rev = requests.get(SPRING_URL + 'account/' + user_id)
        json = util.string_to_json(rev.text)
        if json:
            return json['email']
    except Exception as e:
        print(e)
        error_log(inspect.stack()[0][3], "get username error")
        return None


def get_password(username):
    try:
        rev = requests.get(SPRING_URL + 'api/get_user_id?email=' + username)
        json = util.string_to_json(rev.text)
        return json['password']
    except Exception as e:
        print(e)
        error_log(inspect.stack()[0][3], "get password failed")
        return None


# Return a json from Spring
def create_survey(data):
    # @PostMapping(value="/account/{accountId}/addsurvey")
    url = SPRING_URL + 'account/{0}/addsurvey'.format(current_user.get_id())
    test_log(inspect.stack()[0][3], url)
    rev = requests.post(url, json=data)
    json = util.string_to_json(rev.text)
    return json


def get_all_surveys_for_user(uid):
    '''
    :return a list of survey object string
    '''
    url = SPRING_URL + 'account/' + str(uid) + '/allsurveys'
    test_log(inspect.stack()[0][3], url)
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def get_survey_by_id(surveyId):
    url = SPRING_URL + 'survey?surveyId=' + str(surveyId)
    test_log(inspect.stack()[0][3], url)
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    cur_survey_id = json['id']
    return json


# uuid: link
def get_survey_by_uuid(uuid):
    url = SPRING_URL + 'survey/' + uuid
    test_log(inspect.stack()[0][3], url)
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def create_question(data):
    surveyId = data['surveyId']
    url = SPRING_URL + 'addquestion/' + str(surveyId)
    test_log(inspect.stack()[0][3], url)
    data['surveyId'] = int(surveyId)
    rev = requests.post(url, json=data)
    if rev.status_code == 200:
        print('Rev from POST: ' + url +rev.text)
        return util.string_to_json(rev.text)
    return False


def get_all_general_surveys():
    url = SPRING_URL + 'survey/surveyType/' + 'GENERAL'
    test_log(inspect.stack()[0][3], url)
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def create_answer(answer):
    survey_link = answer['surveyLink']
    url = SPRING_URL + 'answer/' + survey_link
    test_log(inspect.stack()[0][3], url)
    rev = requests.post(url, json=answer)
    if rev.status_code is 200:
        print('Rev from POST : '+ url +rev.text)
        return util.string_to_json(rev.text)
    else:
        error = "[SPRING return error]" + str(rev.status_code)
        return util.string_to_json(rev.text)


def send_invitations(json):
    userId = json['userId']
    surveyId = json['surveyId']
    if userId is not None and surveyId is not None and json['emails'] is not None:
        url = SPRING_URL + 'account/' + userId + "/survey/" + surveyId + "/invitation?emails=" + json['emails']
        test_log(inspect.stack()[0][3], url)
        rev = requests.post(url=url)
        test_log(inspect.stack()[0][3], rev.text)
        return rev.text
    return "Para Error, not sent"


# TODO: get report by survey id
# return json string/object
def get_report_by_id(uid, sid):
    # GET http://localhost:8080/account/1/report/?surveyId=8
    url = (SPRING_URL + 'account/{0}/report/?surveyId={1}'.format(uid, sid))
    test_log(inspect.stack()[0][3], url)
    rev = requests.get(url)
    test_log(inspect.stack()[0][3], rev.text)
    json = util.string_to_json(rev.text)
    return json


if __name__ == '__main__':
    get_user_id("juanchen917@gmail.com")
    get_username("2")
    get_password("juanchen917@gmail.com")
