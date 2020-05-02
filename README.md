# Summary
This repository contains code which will enable you to setup a notification to remind you when to put the bins out and what colour. It is a simple program and will not take into account changes of bin days. However it should be suitable for most of the year.

# Design
The components making up this repository are:
- Lambda function - runs on a schedule, reads a file from S3 to determine the bin colour and publish a message to a SNS topic.
- S3 bucket - contains a single file which contains the next bin colour. This is updated such that it alternates between "Black" and "Green" each week.
- SNS topic - the topic which is used to send notifications out to the user to remind them to put the bins out. This is pre-populated with the email in template.yaml.

# How to configure
Update template.yaml file to put in the email address you want notifications to be sent to. Replace "YOUR_EMAIL_HERE" with this email address.

```
Subscription:
  - Protocol: email
    Endpoint: YOUR_EMAIL_HERE
```

Update template.yaml file to change the day and time of the notification will be sent. At the moment this is configured for 1800 every Tuesday.

```
BinDayNotifierScheduler:
  Type: Schedule
  Properties:
    Schedule: cron(0 18 ? * TUE *)
```

Update any logic in the Python script. At present, the script fetches a file from S3 which has the current week's bin colour. This alternates between "Black" and "Green".

# How to deploy
To run this you will need:
- aws-sam to be installed and configured correctly with all required permissions
- Docker to be installed and running

Deploy with: 
```
sam build --use-container
sam deploy --no-confirm-changeset
```