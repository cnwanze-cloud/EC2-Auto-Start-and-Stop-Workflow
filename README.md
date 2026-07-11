# EC2-Auto-Start-and-Stop-Workflow
A serverless workflow that automatically starts an Amazon EC2 instance, waits for it to boot, performs a health check using AWS Lambda, and either sends a success email or automatically shuts down the instance if the health check fails.
