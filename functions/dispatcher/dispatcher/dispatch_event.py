def dispatch(payload, github_event_type):

    action = payload["action"]
    if github_event_type == "pull_request" and action in ["opened", "reopened"]:
        print("pull request opened")
