def dispatch(action, github_event_type):

    if github_event_type == "pull_request" and action in ["opened", "reopened"]:
        print("pull request opened")
