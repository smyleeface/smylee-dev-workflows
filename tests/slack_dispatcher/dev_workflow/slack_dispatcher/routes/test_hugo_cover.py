import unittest
import urllib.parse
from unittest.mock import patch

import dev_workflow.slack_dispatcher.routes.hugo_cover as hugo_cover


class TestHugoCover(unittest.TestCase):

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
            "text": "hello --world",
            "api_app_id": "A12345",
            "is_enterprise_install": "false",
            "response_url": "https://foobar",
            "trigger_id": "1.2.3",
        }
        self.slack_payload_as_querystring = urllib.parse.urlencode(self.slack_payload)

    @patch("dev_workflow.slack_dispatcher.aws.sns.publish")
    def test_start_send_trigger(self, mock_sns_publish):
        response_url = "https://foobar"
        command_arguments = {
            "repository-name": "cool-repo",
            "pull-request-number": 123,
            "branch-name": "cool-branch",
        }
        ctx = {
            "sns_client": None,
            "response_url": response_url,
            "topic_arn": "arn:aws:sns:us-west-2:123456789012:cool-topic",
        }
        hugo_cover.start(ctx, command_arguments)
        self.assertTrue(mock_sns_publish.called)

    @patch("dev_workflow.slack_dispatcher.slack.utils.post_message")
    def test_start_return_missing_keys(self, mock_post_message):
        response_url = "https://foobar"
        command_arguments = {
            "repository-name": "cool-repo",
            "branch-name": "cool-branch",
        }
        ctx = {
            "sns_client": None,
            "response_url": response_url,
            "topic_arn": "arn:aws:sns:us-west-2:123456789012:cool-topic",
        }
        hugo_cover.start(ctx, command_arguments)
        self.assertTrue(mock_post_message.called)

    def test_missing_values_list(self):
        ctx = {
            "repository-name": "cool-repo",
            "branch-name": "",
            "pull-request-number": 123,
        }
        missing_values = hugo_cover.missing_values_list(ctx)
        self.assertEqual(missing_values, ["branch-name"])
