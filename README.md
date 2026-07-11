# EC2 Auto Start & Health Check Workflow using AWS Step Functions

> A serverless workflow that automatically starts an Amazon EC2 instance, waits for it to boot, performs a health check using AWS Lambda, and either sends a success email or automatically shuts down the instance if the health check fails.

---

## 📖 Project Overview

This project demonstrates how to orchestrate infrastructure automation using **AWS Step Functions** and native **AWS SDK integrations** without writing unnecessary Lambda functions.

The workflow performs the following tasks:

1. Starts an EC2 instance.
2. Waits for the instance to boot.
3. Invokes a Lambda function to verify the EC2 instance is healthy.
4. If the instance is healthy:

   * Sends a success email using Amazon SNS.
5. If the instance is unhealthy:

   * Stops the EC2 instance automatically.


---

# Architecture

```
                ┌─────────────────────┐
                │ Start Execution     │
                └──────────┬──────────┘
                           │
                           ▼
                 Start EC2 Instance
             (AWS SDK Integration)
                           │
                           ▼
                    Wait 120 Seconds
                           │
                           ▼
                Health Check Lambda
                           │
                 ┌─────────┴─────────┐
                 │                   │
          Healthy=True         Healthy=False
                 │                   │
                 ▼                   ▼
      Send Success Email       Stop EC2 Instance
          (Lambda + SNS)      (AWS SDK Integration)
                 │                   │
                 └─────────┬─────────┘
                           ▼
                          End
```
---
<img width="642" height="632" alt="image" src="https://github.com/user-attachments/assets/035072da-5024-4320-aa88-7d8944d1c72a" />

---

# AWS Services Used

* AWS Step Functions
* Amazon EC2
* AWS Lambda
* Amazon SNS
* AWS IAM
* Amazon CloudWatch Logs

---

# Repository Structure

```text
ec2-auto-start-health-check/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── lambda/
│   ├── ec2-health-check/
│   │   └── lambda_function.py
│   │
│   └── send-success-email/
│       └── lambda_function.py
│
├── step-functions/
│   ├── workflow.json
│   └── execution-input.json
│
├── iam/
│   ├── step-functions-policy.json
│   ├── lambda-health-policy.json
│   └── lambda-sns-policy.json
│
├── diagrams/
│   └── architecture.png
│
└── screenshots

```

---

# Step 1 — Launch an EC2 Instance

Launch an EC2 instance with the following configuration:

| Setting        | Value             |
| -------------- | ----------------- |
| AMI            | Amazon Linux 2023 |
| Instance Type  | t2.micro          |
| Security Group | SSH (22)          |
| Optional       | HTTP (80)         |
| Name Tag       | WebServer         |

Copy the **Instance ID**.

Example:

```
i-0123456789abcdef0
```

---

# Step 2 — Create an SNS Topic

1. Open **Amazon SNS**
2. Create a **Standard Topic**
3. Subscribe your email
4. Confirm the subscription

This topic will be used to send success notifications.

---

# Step 3 — Create the IAM Role for the Health Check Lambda

Create a new IAM Role.

### Trusted Entity

```
Lambda
```

Attach the managed policy:

```
AWSLambdaBasicExecutionRole
```

Create an inline policy with the following permissions:

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":[
        "ec2:DescribeInstances"
      ],
      "Resource":"*"
    }
  ]
}
```

Example role name:

```
LambdaHealthCheckRole
```

---

# Step 4 — Create the EC2 Health Check Lambda

Create a Lambda function:

| Setting       | Value            |
| ------------- | ---------------- |
| Runtime       | Python 3.x       |
| Function Name | EC2-Health-Check |

Attach the **LambdaHealthCheckRole**.

Paste the Python code into `lambda_function.py`.

Deploy the function.

---

## Test the Lambda

Create a test event:

```json
{
    "InstanceId":"i-0123456789abcdef0"
}
```

Click **Test**.

Expected output:

```json
{
    "status":"Healthy"
}
```

---

# Step 5 — Create IAM Role for the Email Lambda

Create another Lambda execution role.

Attach:

* AWSLambdaBasicExecutionRole

Create an inline policy allowing:

```text
sns:Publish
```

---

# Step 6 — Create the Send Success Email Lambda

Create another Lambda function.

Function Name

```
EC2-Send-Success-Mail
```

Attach the SNS role.

Deploy the email Lambda.

---

# Step 7 — Create the Step Functions Execution Role

Create a role for AWS Step Functions.

Attach permissions:

```text
ec2:StartInstances

ec2:StopInstances

lambda:InvokeFunction

logs:*

sns:Publish
```

---

# Step 8 — Create the State Machine

Open:

```
AWS Step Functions
```

Create

```
Standard Workflow
```

Name

```
EC2AutoStartWorkflow
```

---

# Step 9 — Start EC2 State

Use the native AWS SDK integration.

Resource

```
arn:aws:states:::aws-sdk:ec2:startInstances
```

Parameters

```json
{
  "InstanceIds":[
      "i-0123456789abcdef0"
  ]
}
```

---

# Step 10 — Wait State

Add a Wait state.

Duration

```
120 Seconds
```

This gives the EC2 instance time to boot.

---

# Step 11 — Health Check Lambda

Add a Lambda Invoke task.

Function

```
EC2-Health-Check
```

Payload

```json
{
    "InstanceId":"i-0123456789abcdef0"
}
```

Output

```text
{% $states.result.Payload %}
```

The Lambda returns:

```json
{
    "status":"Healthy"
}
```

---

# Step 12 — Choice State

After the Lambda task, add a **Choice** state.

### JSONata Condition

```jsonata
{% $states.input.status = 'Healthy' %}
```

If the condition evaluates to **true**, transition to:

```
Send Success Mail
```

Otherwise, use the **Default** transition:

```
Stop EC2 Instance
```

---

# Step 13 — Send Success Email

Invoke the second Lambda.

```
EC2-Send-Success-Mail
```

End the workflow.

---

# Step 14 — Stop EC2 Instance

Use another AWS SDK Integration.

Resource

```
arn:aws:states:::aws-sdk:ec2:stopInstances
```

Parameters

```json
{
  "InstanceIds":[
      "i-0123456789abcdef0"
  ]
}
```

End the workflow.

---

# Step 15 — Enable CloudWatch Logging

Inside the Step Function:

Enable

```
CloudWatch Logs
```

Log Level

```
ALL
```

This records:

* State transitions
* Inputs
* Outputs
* Errors
* Retries

---

# Step 16 — Test the Workflow

Start a new execution.

Execution input:

```json
{
    "InstanceId":"i-0123456789abcdef0"
}
```

---

## Successful Execution

```
Start EC2
      │
      ▼
Wait 120 Seconds
      │
      ▼
Health Check
      │
      ▼
Healthy?
      │
      ▼
Send Success Mail
      │
      ▼
End
```

---

## Failed Health Check

```
Start EC2
      │
      ▼
Wait 120 Seconds
      │
      ▼
Health Check
      │
      ▼
Healthy?
      │
      ▼
Stop EC2
      │
      ▼
End
```

---

# Step 17 — Simulate a Failure

Modify the Health Check Lambda to return:

```python
return {
    "status":"Unhealthy"
}
```

Execute the workflow again.

Expected behavior:

* EC2 starts
* Waits 120 seconds
* Health check fails
* EC2 instance stops automatically

---

# Step 18 — View CloudWatch Logs

Open:

```
CloudWatch
```

Navigate to:

```
Log Groups
```

Open the Step Functions log group.

Observe:

* State transitions
* Lambda outputs
* Execution duration
* Errors
* Retries

---

# Verify Email Notification

If the health check passes, the SNS topic sends an email similar to:

**Subject**

```
EC2 Workflow
```

**Message**

```
EC2 instance started successfully.

Health check passed.

Workflow completed successfully.
```
---

## Author

**Your Name**

Cloud Engineer | AWS Practitioner | DevOps Enthusiast
