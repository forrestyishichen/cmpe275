import json as JSON
from flask import json

request_json = None

ERROR_LOG = __name__ + ' juanchen: '


def request_form_to_json(request):
    try:
        return JSON.loads(json.dumps(request.form))
    except Exception:
        print(ERROR_LOG + 'request form to json failed')
        return None


def string_to_json(json_str):
    try:
        return JSON.loads(json_str)
    except Exception:
        print(ERROR_LOG + 'string to json failed')
        return None


def json_to_string(json_obj):
    try:
        return JSON.dumps(json_obj)
    except Exception:
        print(ERROR_LOG + 'json to string failed')
        return None


def stringlist_to_json_list(data):
    try:
        options = []
        for choice in data.split(';'):
            options.append({'content': choice})
        return options
    except Exception:
        print(ERROR_LOG + 'string list to json list failed')
        return None


def extract_survey_json(survey):
    # input: json format survey
    try:
        if survey['questions']:
            for question in survey['questions']:
                if question['questionContent']:
                    content = question['questionContent']['questionContent']
                    question['questionContent'] = stringlist_to_json_list(content)
        print(survey)
        return survey
    except Exception:
        return None


def statis_to_json_list(statis, questionContent):
    try:
        options = []
        stat = []
        res = []
        for count in statis.split(';'):
            stat.append(count)
        print(stat)
        for choice in questionContent.split(';'):
            options.append(choice)
        print(options)
        for i in range(len(options)):
            res.append({'content': options[i], 'count': stat[i]})
        print(res)
        return res
    except Exception:
        print(ERROR_LOG + 'string list to json list failed')
        return None


def extract_report_json(survey):
    # input: json format survey
    try:
        if survey['questions']:
            for question in survey['questions']:
                statis = question['statistic']
                if question['questionContent']:
                    content = question['questionContent']['questionContent']
                    question['questionContent'] = statis_to_json_list(statis, content)
            print(survey)
            return survey
    except Exception as e:
        print(e)
        return None

# {'10.answerContent': 'yes', '20.answerContent': 'cookie', '21.answerContent.Japan': 'Japan',
# '21.answerContent.Korea': 'Korea', '22.answerContent': 'female', '23.answerContent.engineer': 'engineer',
# '23.answerContent.freelancer': 'freelancer', '8.answerContent': 'Anything you like.', 'action': 'save_answer',
# 'username': 'juanchen917@gmail.com'}
def parse_answer_json(json):
    res = {}
    for k, v in json.items():
        if len(k.split('.')) > 1:
            tmp_key =k.split('.')[0]
            if tmp_key not in res:
                res[tmp_key] = []
            res[tmp_key].append(v)
        else:
            res[k] = v
# {'10': ['yes'], '20': ['cookie'], '21': ['China', 'Japan'], '22': ['female'], '23': ['engineer'],
#              '8': ['nohting to say'], 'action': 'save_answer', 'username': 'juanchen917@gmail.com'}

    print(res)
    answer = {}
    questions = []
    for k,v in res.items():
        if type(v) is list:
            question = {}
            question['questionId'] = int(k)
            question['answerContent'] = ';'.join(v)
            questions.append(question)
        else:
            if k == 'username':
                answer['email'] = v
            else:
                answer[k] = v
    answer['aq'] = questions
    return answer













