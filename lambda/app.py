import boto3
from botocore.exceptions import ClientError
import os
import datetime

def run(event, context):
    try:
        topicARN = os.environ.get("TOPIC_ARN")
        bucketName = os.environ.get("BUCKET_NAME")
        snsClient = boto3.client('sns')
        s3Client = boto3.client('s3')

        # 1 = Tuesday, 3 = Thursday
        today = datetime.datetime.today().weekday()
        print("Today is {}. Where Monday = 0".format(today))
        if today is 1:
            # check for black/green bin
            try:
                response = s3Client.get_object(Bucket=bucketName, Key="wednesday-bin.txt")
                contents = response["Body"].read().decode('utf-8')
                print("Contents of wednesday-bin.txt is: {}".format(contents))

                if contents == "Green":
                    print("Bin is Green")
                    s3Client.put_object(Bucket=bucketName, Key="wednesday-bin.txt", Body="Black")
                    
                    print("Publishing message that bin is Green")
                    # set s3 object to "Black"
                    snsClient.publish(
                        TopicArn=topicARN,
                        Subject="Bin notification",
                        Message="Green bin is due out tomorrow."
                    )
                    print("Published message that bin is Green")
                elif contents == "Black":
                    print("Bin is Black")
                    s3Client.put_object(Bucket=bucketName, Key="wednesday-bin.txt", Body="Green")

                    print("Publishing message that bin is Black")
                    # set s3 object to "Black"
                    snsClient.publish(
                        TopicArn=topicARN,
                        Subject="Bin notification",
                        Message="Black bin is due out tomorrow."
                    )
                    print("Published message that bin is Black")
                else:
                    print("Bin is not Black or Green")
                    raise Exception("Unknown contents of 'wednesday-bin.txt'")
            except ClientError as ex:
                print("Client error!")
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    print("S3 error occurred most likely trying to get config file", ex)
                    snsClient.publish(
                        TopicArn=topicARN,
                        Subject="Bin notification",
                        Message="Green or black bins are due out tomorrow. Please populate 'wednesday-bin.txt' in S3 bucket ready for next week."
                    )
                else:
                    print("Unknown error occurred:", ex)
                    snsClient.publish(
                        TopicArn=topicARN,
                        Subject="Bin notification",
                        Message="Green or black bins are due out tomorrow. Error occurred, please check AWS account."
                    )
        elif today == 3:
            # check for brown bin
            try:
                s3Client.get_object(Bucket=bucketName, Key="brown-bin.txt")

                snsClient.publish(
                    TopicArn=topicARN,
                    Subject="Bin notification",
                    Message="Brown bin is due out tomorrow."
                )
                print("Published message that bin is Brown")
                
                
                s3Client.delete_object(Bucket=bucketName, Key="brown-bin.txt")

                print("Deleted brown-bin.txt")
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    print("brown-bin.txt does not exist. No brown bin this week.")
                    s3Client.put_object(Bucket=bucketName, Key="brown-bin.txt", Body="Brown")

                else:
                    print("Unknown error occurred:", ex)
                    snsClient.publish(
                        TopicArn=topicARN,
                        Subject="Bin notification",
                        Message="Green or black bins are due out tomorrow. Error occurred, please check AWS account."
                    )

        print("Returning All OK")
        return "All OK"
    except Exception as e:
        print("Error occurred: ", e)
        return e