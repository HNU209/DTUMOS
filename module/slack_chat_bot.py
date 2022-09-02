import json
import sys
import requests

def send_msg(msg, msg_title='Lab-computer MSG'):
    url = 'https://hooks.slack.com/services/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'
    message = (f'\n{msg}') 
    title = (f"{msg_title}") # 타이틀 입력
    slack_data = {
        "username": "Lab-Chat-Bot", # 보내는 사람 이름
        "icon_emoji": ":satellite:",
        "channel" : "#msg",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)