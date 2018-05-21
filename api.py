
import requests
import util
from flask_login import current_user

TEST_LOG = __name__ + ' juanchen : '

ERROR_LOG = __name__ + ' juanchen_ERROR : '

SPRING_URL = 'http://ec2-35-174-138-128.compute-1.amazonaws.com:8080/'

cur_survey_id = None


def register_request(data):
    try:
        print(TEST_LOG + data)
        rev = requests.post(SPRING_URL + 'register', data=data)
        print(TEST_LOG + rev.text)
        if rev.text == 'fail':
            return False
        else:
            return True
    except Exception:
        print(ERROR_LOG + 'register failed')
        return False


def get_code(email):
    try:
        rev = requests.get(SPRING_URL+'email_verify?email='+email)
        print(TEST_LOG+rev.status_code)
        if rev.status_code == 200:
            return True
        print(TEST_LOG+rev.text)
        return False
    except Exception:
        print(ERROR_LOG + 'Get Code Error')
        return False


def register_user(data):
    try:
        email = data['username']
        code = data['code']
        password = data['password']
        rev = requests.post(SPRING_URL+'signup?email='+email+'&code='+code+'&password='+password)
        if rev.status_code == 200:
            return True
        print(ERROR_LOG + rev.text)
        return False
    except Exception:
        print(ERROR_LOG + 'register failed')
        return False


def get_user_id(username):
    try:
        rev = requests.get(SPRING_URL + 'api/get_user_id?email=' + username)
        json = util.string_to_json(rev.text)
        print(json)
        return str(json['id'])
    except Exception:
        print(ERROR_LOG + 'get user id failed')
        return None


def get_username(user_id):
    try:
        rev = requests.get(SPRING_URL + 'account/' + user_id)
        json = util.string_to_json(rev.text)
        if json:
            return json['email']
    except Exception:
        print(ERROR_LOG + 'get username error')
        return None


def get_password(username):
    try:
        rev = requests.get(SPRING_URL + 'api/get_user_id?email=' + username)
        json = util.string_to_json(rev.text)
        # print(json['password'])
        return json['password']
    except Exception:
        print(ERROR_LOG + 'get password failed')
        return None


# Return a json from Spring
def create_survey(data):
    # @PostMapping(value="/account/{accountId}/addsurvey")
    url = SPRING_URL + 'account/{0}/addsurvey'.format(current_user.get_id())
    print (url)
    print (type(data))
    print (data)
    rev = requests.post(url, json=data)
    print (rev.text)
    json = util.string_to_json(rev.text)
    return json


def get_all_surveys_for_user(uid):
    '''
    :return a list of survey object string
    '''
    url = SPRING_URL + 'account/' + str(uid) + '/allsurveys'
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def get_survey_by_id(surveyId):
    url = SPRING_URL + 'survey?surveyId=' + str(surveyId)
    print(url)
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    cur_survey_id = json['id']
    return json


# uuid: link
def get_survey_by_uuid(uuid):
    url = SPRING_URL + 'survey/' + uuid
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def create_question(data):
    surveyId = data['surveyId']
    url = SPRING_URL + 'addquestion/' + str(surveyId)
    data['surveyId'] = int(surveyId)
    print('Send request to POST ' + url)
    rev = requests.post(url, json=data)
    if rev.status_code is 200:
        print('shi: '+rev.text)
        return util.string_to_json(rev.text)
    return False


def get_all_general_surveys():
    url = SPRING_URL + 'survey/surveyType/' + 'GENERAL'
    rev = requests.get(url)
    json = util.string_to_json(rev.text)
    return json


def create_answer(answer):
    survey_link = answer['surveyLink']
    url = SPRING_URL + 'answer/' + survey_link
    print('[Requests]: send to POST ' + url)
    rev = requests.post(url, json=answer)
    if rev.status_code is 200:
        print('shi: '+rev.text)
        return util.string_to_json(rev.text)
    else:
        error = "[SPRING return error]" + str(rev.status_code)
        return util.string_to_json(rev.text)


def send_invitations(json):
    userId = json['userId']
    surveyId = json['surveyId']
    if userId is not None and surveyId is not None and json['emails'] is not None:
        url = SPRING_URL + 'account/' + userId + "/survey/" + surveyId + "/invitation?emails=" + json['emails']
        rev = requests.post(url=url)
        print(rev.text)
        return rev.text
    return "Para Error, not sent"


# TODO: get report by survey id
# return json string/object
def get_report_by_id(uid, sid):
    # GET http://localhost:8080/account/1/report/?surveyId=8
    url = (SPRING_URL + 'account/{0}/report/?surveyId={1}'.format(uid, sid))
    rev = requests.get(url)
    print(TEST_LOG+rev.text)


if __name__ == '__main__':
    get_user_id("juanchen917@gmail.com")
    get_username("2")
    get_password("juanchen917@gmail.com")
