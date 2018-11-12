#Automated Cloudwatch log archival
Cloudwatch logs are archived in S3 and the the process is automated with help of a Step function. 
Lambda function consists the logic to create the export task. 
Cloduwatch event is created to trigger the step function daily.
