import json
import requests
import urllib.parse


def parse_query_string(query_string):
    parsed_query = urllib.parse.parse_qs(query_string)
    parsed_query_single_values = {k: v[0] for k, v in parsed_query.items()}
    return parsed_query_single_values


def get_action(parsed_json):
    requested_text = parsed_json.get("text", "")
    return requested_text.split(' ', 1)[0]


def post_message(url, data):
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.status_code
    except Exception as e:
        print(f"Error sending message to Slack: {e}")
        exit(1)


def get_command_arguments(command_text):
    split_args = command_text.split("--")[1:]
    result_dict = {}
    missing_values = []
    for split_arg in split_args:
        key, value = split_arg.split('=')
        if value is None or len(value.strip()) == 0:
            missing_values.append(key)
        else:
            key = key.lstrip('-')
            value = int(value) if value.isdigit() else value.strip()
            result_dict[key] = value
    return result_dict, missing_values


def send_command_received_message(response_url):
    payload_to_send = {
        "text": "Request received. Processing...",
        "response_type": "in_channel"
    }
    post_message(response_url, payload_to_send)
