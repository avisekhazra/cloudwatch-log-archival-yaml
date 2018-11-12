import boto3
from datetime import datetime

##Intialize the clients
sts_client = boto3.client('sts');

## Lambda Handler
def lambda_handler(event, context):
    token = '0';
    if "nextToken" in event:
        token = event['nextToken'];
    nextToken = event.get("nextToken", '')
    region = event.get("region", 'us-east-1')

    try:
        roleObj = {"np":"arn:aws:iam::99999999:role/IAM-NON-PROD-ROLE"}
        responseCredentials = getAWSCredentials(roleObj[event.get('env', 'np')],"stsLogArchiveSession")
        cloudwatch_client = boto3.client('logs', **responseCredentials, region_name='us-east-1')
        log_group = get_cloudwatch_log_groups(event,token,client,1);
        client.put_retention_policy(logGroupName = log_group, retentionInDays=14 )
        prefix = '';
        now = datetime.now();
        prefix = '/'+str(now.year)+'-'+ str(now.month) + '-'+str(now.day);
        if(describe_s3_export_tasks(cloudwatch_client) > 0):
               event["delay"] = True
               event["nextToken"] = token
        else:
               create_s3_export_task(client,tags["servicename"],prefix,log_group,event)
    except Exception as e:
      print(e);
    return event;

## Get the STS credentials for the role 
def getAWSCredentials(Role_Arn, Role_Session_Name):
    response = sts_client.assume_role(
    RoleArn=Role_Arn,
    RoleSessionName=Role_Session_Name,
    DurationSeconds=900
    )
    return{
    "aws_access_key_id": response["Credentials"]["AccessKeyId"],
    "aws_secret_access_key": response["Credentials"]["SecretAccessKey"],
    "aws_session_token": response["Credentials"]["SessionToken"]
    }
    
## Get the cloudwatch log group
def get_cloudwatch_log_groups(event,token,client,limit):
    event["delay"] = False;
    if token =='0':
      response = client.describe_log_groups(
       limit=limit
      );
    else:
       response = client.describe_log_groups(
       nextToken=token,
       limit=limit
      );
    if "nextToken" in response:
        event["nextToken"] = response["nextToken"];
        event["continue"] = True;
    else:
        event["continue"] = False;
    print(event)
    return response["logGroups"][0]["logGroupName"]

## Create S3 export task for the logs groups created in for last 24 hours.  
    
def create_s3_export_task(cloudwatch_client,service,resource, log_group,event):
    now = datetime.now();
    date_time_now= now;
    date_time_today = datetime(date_time_now.year,date_time_now.month,date_time_now.day);
    date_time_yesterday = datetime(date_time_now.year,date_time_now.date_time_now,date_time.day-1)
    log_group_folder_name =log_group.replace("/","_");
    response = cloudwatch_client.create_export_task(
       fromTime=int(date_time_yesterday.timestamp()*1000),
       to=int(date_time_today.timestamp()*1000),
       logGroupName = log_group,
       destination='log-archive',
       destinationPrefix=event.get('env','np') + '/' + log_group_folder_name
    )

## Fetch the running Export tasks in the account.
def describe_s3_export_tasks(cloudwatch_client):
    response = len(cloudwatch_client.describe_export_tasks(statusCode='PENDING')["exportTasks"])
    response += len(cloudwatch_client.describe_export_tasks(statusCode='RUNNING')["exportTasks"])
    return response
    
