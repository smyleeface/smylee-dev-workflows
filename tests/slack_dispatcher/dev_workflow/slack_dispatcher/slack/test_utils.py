import unittest
import urllib.parse

import dev_workflow.slack_dispatcher.slack.utils as slack_utils


class TestSlackDispatcher(unittest.TestCase):

    def setUp(self):
        self.slack_payload = {
            "token": "abc123",
            "team_id": "T12345",
            "team_domain": "cool team domain",
            "channel_id": "C12345",
            "channel_name": "cool channel name",
            "user_id": "U12345",
            "user_name": "cool user name",
            "command": "/cool-command",
            "text": "hello --world=foobar --baz= --bat=123",
            "api_app_id": "A12345",
            "is_enterprise_install": "false",
            "response_url": "https://foobar",
            "trigger_id": "1.2.3"
        }
        self.slack_payload_as_querystring = urllib.parse.urlencode(self.slack_payload)

    def test_parse_query_string(self):
        parsed_query = slack_utils.parse_query_string(self.slack_payload_as_querystring)
        self.assertEqual(parsed_query, self.slack_payload)

    def test_get_action(self):
        self.assertEqual(slack_utils.get_action(self.slack_payload), "hello")

    def test_get_command_arguments(self):
        args, missing = slack_utils.get_command_arguments(self.slack_payload.get("text"))
        self.assertEqual(args, {"bat": 123, "world": "foobar"})
        self.assertEqual(missing, ["baz"])


