import boto3

def lambda_handler(event, context):
    sns = boto3.client('sns')
    topic_arn = "arn:aws:sns:us-east-1:021655151277:MyTopic" 
    
    message = f"Success! The EC2 Instance {event.get('InstanceId')} has started and passed the health check."
    
    sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="EC2 Workflow Success Notification"
    )
    return {"message": "Notification sent successfully!"}