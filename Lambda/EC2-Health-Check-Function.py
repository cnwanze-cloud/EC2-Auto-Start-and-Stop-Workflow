import boto3

def lambda_handler(event, context):
    # Retrieve Instance ID passed from Step Functions
    instance_id = event.get('InstanceId')
    ec2 = boto3.client('ec2')
    
    try:
        # Check if instance is actually running
        response = ec2.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        if state == 'running':
            return {"status": "Healthy"}
        else:
            return {"status": "Unhealthy"}
    except Exception as e:
        return {"status": "Unhealthy", "error": str(e)}