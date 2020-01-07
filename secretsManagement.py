#
# Functions to manage the secrets in AWS Secrets Manager
#

from botocore.exceptions import ClientError
import cgi
import boto3
import settings
import json
import datetime
import miscFunctions
import logFunctions
import slackFunctions
import urllib
import s3Functions

requestContext = {}

#
# AWS Functions
#

session = boto3.session.Session()
client = session.client( service_name='secretsmanager', region_name=settings.region )

def aws_secretsmanager_get_secret(SecretId1): # Decrypts secret using the associated KMS CMK.
    try:
        answer = client.get_secret_value( SecretId=SecretId1 )
        return json.loads(answer.get('SecretString', '{}'))

    except:
        return {}

def aws_secretsmanager_set_secret(SecretId1, SecretValue1, Tags1 = []):
    try:
        answer = client.create_secret( Name=SecretId1, Description='Created by '+settings.botName, SecretString=SecretValue1, Tags=Tags1 )
        return 'Name' in answer
    except Exception as e:
        logFunctions.log('Error when saving a secret: '+str(e))
        return False

def aws_secretsmanager_update_secret(SecretId1, SecretValue1):
    try:
        answer = client.update_secret( SecretId=SecretId1, Description='Created by '+settings.botName, SecretString=SecretValue1 )
        return 'Name' in answer
    except:
        return False

#
# Secret Management Actions
#

def HTML_uploadForm(url):
    form = """<html>
    <head>
    <title>Secret File Upload</title>
    <script src="https://code.jquery.com/jquery-latest.min.js"></script>
    <script type="text/javascript">
    $(document).ready(function(){

        prisigned_url='"""+url+"""'
        $(function() { $('#theButton').on('click', sendFile); });

        function sendFile(e) {
            e.preventDefault();
            document.getElementById('msg').innerText='uploading...';
            document.getElementById('theForm').style.display='none';
            var theFormFile = $('#theFile').get()[0].files[0];
            $.ajax({
                type: 'PUT',
                url:prisigned_url,
                //contentType: 'binary/octet-stream',
                contentType: '"""+settings.S3_content_type+"""',
                processData: false,
                data: theFormFile,
                xhr: function() {
                    var myXhr = $.ajaxSettings.xhr();
                    if(myXhr.upload){
                        myXhr.upload.addEventListener('progress',progress, false);
                    }
                    return myXhr;
                }
            })
            .success(function(file,response) {
                document.getElementById('msg').innerHTML='<font color=green>File uploaded</font>';
            })
            .error(function() {
                document.getElementById('msg').innerHTML='<font color=red>File NOT uploaded</font>';
            });
            return false;
        }
    });

    function progress(e){
        if(e.lengthComputable){
            var Percentage = (e.loaded * 100)/e.total;
            document.getElementById('msg').innerHTML='uploading...<br>'+Math.round(Percentage)+'%';
        }
    }
    </script>
    </head>
    <body>
    <center>
    <h2 id=msg>Select the file to upload</h2>
    <form id="theForm" method="POST" enctype="multipart/form-data" >
        <input id="theFile" name="file" type="file"/> 
        <button id="theButton" type="button" >Send</button>
    </form>
    </center>
    </body>
    </html>
    """
    # code from : https://github.com/boto/boto3/issues/1149
    return form


def uploadURL(requestContext, preSignedURL):
    myURL = "https://" + requestContext.get('domainName', '') + requestContext.get('path', '/')
    return myURL + "/?presigned="+urllib.parse.quote_plus(preSignedURL)


def encode_text_secret(secret):
    return json.dumps( {"secretType": "string", "secret": secret} )

def prepare_s3file_secret(old_secret_value = {}):
    old_secret_value["secretType"] = "s3file"
    old_secret_value["secret"] = miscFunctions.generate_unique_id()+'.dat'
    return old_secret_value

def set_secret(user, team, channel, secret_name, secret_value):
    if secret_name != '':
        try:
            Tags1 = [
                {'Key': 'CreatedBy', 'Value': user},
                {'Key': 'CreatedDate', 'Value': datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}
            ]
            if secret_value.strip() == '+': # it's a file-secret
                secret_data = prepare_s3file_secret()
                if aws_secretsmanager_set_secret(team+'.'+channel+'.'+secret_name, json.dumps(secret_data), Tags1):
                    presignedURL = s3Functions.create_presigned_url_put( secret_data["secret"] )
                    logFunctions.log('User '+user+' created the file secret: "'+secret_name+'" (file upload pending) at channel: '+channel)
                    return '*Please, use the link below to upload your file*:\r`'+uploadURL(requestContext, presignedURL)+'`'
                else:
                    return 'Something went wrong when preparing your filesecret'
            else:
                if aws_secretsmanager_set_secret(team+'.'+channel+'.'+secret_name, encode_text_secret(secret_value), Tags1):
                    logFunctions.log('User '+user+' created the secret: "'+secret_name+'" at channel: '+channel)
                    fret = 'I will remember it as '+slackFunctions.escape(secret_name)+' (only for this channel)'
                    if settings.check_private_channel:
                        fret += slackFunctions.get_channel_info(channel)
                    return fret
                else:
                    return 'Something went wrong when storing your secret'
        except Exception as e:
            return 'Error. Secret not stored. '+slackFunctions.escape(str(e))
    else:
        return 'I need a name and a value to remember it!'

def update_secret(user, team, channel, secret_name, secret_value, old_secret_value):
    if secret_name != '':
        try:
            SecretId1 = team+'.'+channel+'.'+secret_name
            if secret_value.strip() == '+': # it's a file-secret
                secret_data = prepare_s3file_secret(old_secret_value)
                if aws_secretsmanager_update_secret(SecretId1, json.dumps(secret_data)):
                    presignedURL = s3Functions.create_presigned_url_put( secret_data["secret"] )
                    logFunctions.log('User '+user+' updating the file secret: "'+secret_name+'" (file upload pending) at channel: '+channel)
                    return '*Please, use the link below to upload your new file*:\r`'+uploadURL(requestContext, presignedURL)+'`'
                else:
                    return 'Something went wrong when preparing your filesecret for update'
            else:
                if aws_secretsmanager_update_secret(SecretId1, encode_text_secret(secret_value)):
                    client.tag_resource( SecretId=SecretId1, Tags=[
                            {'Key': 'ModifiedBy', 'Value': user},
                            {'Key': 'ModifiedDate', 'Value': datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}
                        ]
                    )

                    logFunctions.log('User '+user+' updated the secret: "'+secret_name+'" at channel: '+channel)
                    fret = 'I will remember the new "'+slackFunctions.escape(secret_name)+'" secret'
                    if settings.check_private_channel:
                        fret += slackFunctions.get_channel_info(channel)
                    return fret
                else:
                    return 'Something went wrong when updating your secret'
        except Exception as e:
            return 'Error. Secret not updated. '+slackFunctions.escape(str(e))
    else:
        return 'I need a name and a value to update it!'


def get_secret(user, team, channel, secret_name = ''):
    SecretId1=team+'.'+channel+'.'+secret_name
    oSecret = aws_secretsmanager_get_secret( SecretId1 )
    if len(oSecret) > 0:
        # tag the secret
        client.tag_resource( SecretId=SecretId1, Tags=[
                {'Key': 'AccessedBy', 'Value': user},
                {'Key': 'AccessedDate', 'Value': datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}
            ])
        logFunctions.log('User '+user+' requested the secret: "'+secret_name+'" at channel: '+channel)
        if oSecret.get('secretType', '') == 'string':
            return 'Your secret is: `'+slackFunctions.escape(oSecret.get('secret', '')+'`')
        elif oSecret.get('secretType', '') == 's3file':
            s3url = s3Functions.create_presigned_url_get(oSecret.get('secret', ''), oSecret.get('original-file-name', secret_name))
            return '*Download your secret from here*:\r`'+slackFunctions.escape(s3url)+ '`\rThe link expires in 30 minutes'
        else:
            return 'unknown secret type'
    else:
        return 'Secret not found'

def delete_secret(user, team, channel, secret_name):
    try:
        SecretId1=team+'.'+channel+'.'+secret_name
        client.tag_resource( SecretId=SecretId1, Tags=[
                {'Key': 'DeletedBy', 'Value': user},
                {'Key': 'DeletedDate', 'Value': datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}
            ]
        )
        answer = client.delete_secret(SecretId=SecretId1 )
        if 'Name' in answer:
            logFunctions.log('User '+user+' deleted the secret: "'+secret_name+'" at channel: '+channel)
            return "I will no longer remember "+slackFunctions.escape(secret_name)
        else:
            return 'Sorry, there was a problem deleting your secret'
    except Exception as e:
            return 'Sorry, there was a big problem deleting your secret: '+slackFunctions.escape(str(e))


def get_secret_list(team, channel):
    secrets = []
    prefix = team+'.'+channel+'.'
    try:
        if settings.check_private_channel:
            info = slackFunctions.get_channel_info(channel)
        else:
            info = ''
        answer = client.list_secrets( MaxResults=64 )
        while 'SecretList' in answer:
            for sec in answer['SecretList']:
                if 'Name' in sec:
                    if sec['Name'][:len(prefix)] == prefix:
                        secret = sec['Name'][len(prefix):]
                        secrets.append(secret)
            if ('NextToken' in answer) and (answer['NextToken'] is not None):
                answer = client.list_secrets( MaxResults=64, NextToken=answer['NextToken'] )
            else:
                answer = {}
        if len(secrets) == 0:
            return 'I have no secrets'+info
        else:
            textSecrets = "I have "+str(len(secrets))+" secrets\n"
            for iSecret in secrets:
                textSecrets+= '> • '+slackFunctions.escape(iSecret)+"\n"
            return textSecrets+info
    except Exception as e:
            return 'Error getting the secrets list: '+str(e)

def get_secret_list_extended(team, channel):
    secrets = []
    prefix = team+'.'+channel+'.'
    try:
        if settings.check_private_channel:
            info = slackFunctions.get_channel_info(channel)
        else:
            info = ''
        answer = client.list_secrets( MaxResults=64 )
        while 'SecretList' in answer:
            for sec in answer['SecretList']:
                if 'Name' in sec:
                    if sec['Name'][:len(prefix)] == prefix:
                        secret = {}
                        secret['Tags'] = {}
                        if 'Tags' in sec: # check if there are tags
                            for tag in sec['Tags']:
                                if 'Key' in tag:
                                    secret['Tags'][tag['Key']] = tag['Value']
                        secret['Name'] = sec['Name'][len(prefix):]
                        secrets.append(secret)
            if ('NextToken' in answer) and (answer['NextToken'] is not None):
                answer = client.list_secrets( MaxResults=64, NextToken=answer['NextToken'] )
            else:
                answer = {}
        if len(secrets) == 0:
            return 'I have no secrets'+info
        else:
            textSecrets = "I have "+str(len(secrets))+" secrets\n"
            for iSecret in secrets:
                textSecrets+= '> • *'+slackFunctions.escape(iSecret['Name'])+'* '+slackFunctions.escape(str(iSecret['Tags']))+"\n"
            return textSecrets+info
    except Exception as e:
            return 'Error getting the detailed secrets list: '+str(e)
