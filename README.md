# Security Minion

A serverless bot to provide secrets managment for collaboration platforms (currently supports slack)

- Uses AWS secrets manager to manage secrets 
- Allows storage and access to secrets on a slack channel context basis
- Sends audit logs to AWS CloudWatch
- Warns if the channel isn't private


## Getting Started

See deployment for notes on how to deploy the Security Minion bot.

### Prerequisites

- An AWS account and a user with permissions for Lambda function, Secrets Manager and S3.
- A Slack account and a user with admin access to Slack


### Deployment

#### AWS

**create a Lambda function**  
- Open the [AWS Lambda console](https://console.aws.amazon.com/lambda/home).
- Choose Create a function.
- For Function name, enter sminion
- Choose Create function.

**Prepare the deployment package**  
On a computer with Python, create a new directory, clone this project repository and install all dependency modules local to the project using the following command:  
pip3 install -t . -r requirements.txt

Update settings.py to reflect the correct AWS region

**Manually build a deployment package**  
- Zip up the project folder for deployment to Lambda. If you are running Linux or macOS, use the following command:
- zip -r ../sminion.zip .
- if running Windows, use your favorite zipping tool.

**Upload deployment package to your Lambda function**  
Open the AWS Lambda console.
- Choose Functions on the navigation pane, and then open your function.
- In the Function code section, expand the Code entry type drop-down list, and then choose Upload a .ZIP file.
- Choose Upload, and then select your .zip file.
- Choose Save.
- Choose Test.


Use **Python 3.7** and set **lambda_function.main** for the Handler value.

The API gateway method can be "**GET** and **POST**" or just **ANY**. Write down the API endpoint for the next part.

Finally add permissions to the IAM Role: **SecretsManagerReadWrite**, **CloudWatchLogsFullAccess** and read/write in the bucket

Set the S3 bucket **CORS** configuration:  
<?xml version="1.0" encoding="UTF-8"?>  
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">  
<CORSRule>  
    <AllowedOrigin>*</AllowedOrigin>  
    <AllowedMethod>GET</AllowedMethod>  
    <AllowedMethod>PUT</AllowedMethod>  
    <MaxAgeSeconds>3000</MaxAgeSeconds>  
    <AllowedHeader>*</AllowedHeader>  
</CORSRule>  
</CORSConfiguration>


---

#### SLACK
Login to Slack with admin permissions. Go to [slack API](https://api.slack.com/apps) and create a new app

##### Go to **"Slash Commands"** and create a command with these details:
- __Command__: /sminion
- __Request URL__: Enter the **API gateway endpoint**. It should look like: https://jxy71wvxga.execute-api.eu-west-1.amazonaws.com/default/sminion
- __Short Description__: keeps your secrets in this channel
- __Usage Hint__: secret[=value] | ? | ??

and save it.

Now, from "App Credentials" in the "Basic Information" section, copy the value of **Verification Token** and create an environment variable named **"VerificationToken"** in the lamba function settings with that value.  
Also add the **BucketName** environment variable with the proper S3 bucket to store secret files.  
In **"Bot Users"** add a bot: enter a name and set **"Always Show My Bot as Online"** to **ON**.  
Go to **"OAuth & Permissions"** and click **"Install App in WorkSpace"**, click **"Allow"**, copy the value of **"Bot User OAuth Access Token"** and set an environment variable named **"BotUserOAuthAccessToken"** in the lamba function settings with that value.  
Go to the slack app, create a channel or select one with the people that will use the app and **add** the **app**.




---

## Notes
1. The logs can be accessed at CloudWatch, Log Groups, /aws/lambda/__FUNCTION_NAME__
2. At AWS secrets manager, the secrets are named: __TEAMID.CHANNELID.SECRETNAME__


## Built With

* Python 3.7



## Authors

* **Sebastian Sejzer**
* **Guy Halfon**


# **Usage**

- /sminion help returns this message
- /sminion ? returns a list of secrets stored for this channel
- /sminion ?? returns a detailed list of secrets stored for this channel
- /sminion secret-name returns the stored secret
- /sminion secret-name=secret-value saves or updates a secret-value as secret-name
- /sminion secret-name.txt=+ advanced mode to save a secret. It allows you to upload a file.
- /sminion <tags:{tag1=value,tag2=value}> secret=secret-value (not yet implmented)


# **Todo**
- support file uploads (to s3)
- support tags
- add switch to block/delete secrets if a channel goes public
- support for microsoft teams
- run more extensive PT
- delete the associated S3 file when the secret is deleted

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Omri Palmon and Ori Livnat from Weka.io - Design,Requirements & Testing

![NOX90](https://www.devseccon.com/tel-aviv-2018/wp-content/uploads/sites/11/2018/05/nox90-2.png "NOX90 secret manager bot for Slack")
