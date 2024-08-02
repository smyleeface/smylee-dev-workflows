def publish(sns_client, topic_arn, message):
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
        )
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
