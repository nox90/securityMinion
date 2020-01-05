#
# Main Lambda Function for the Security Minion
#

import os
import time
import re
import json
import urllib
import datetime
import boto3
import base64

import logFunctions
import secretsManagement
import settings



verificationToken = os.environ.get('VerificationToken')


isBase64Encoded = False

def main(event, context):
    return_headers = {}
    output = ''
    slack_event = {"type": ""}

    try: # load the request context
        secretsManagement.requestContext = event.get('requestContext', {})
    except:
        secretsManagement.requestContext = {}


    try: # load the GET parameters
        get_params = event.get('queryStringParameters', '{}')
    except:
        get_params = {}

    try: # load JSON post
        jsonbody = json.loads(event.get('body', {}))
    except Exception as e:
        jsonbody = {}
        try: # it's not JSON. lets try to decode it as URL with multiple query string 
            if 'body' in event:
                bodyString = event['body']
            else:
                bodyString = ''
            if ('isBase64Encoded' in event) and event['isBase64Encoded']:
                slack_event = base64.decodestring(bytes(bodyString, 'utf-8')).decode('utf-8')
                slack_event = urllib.parse.parse_qs(slack_event)
            else:
                slack_event = urllib.parse.parse_qs(bodyString)
        except Exception as e:
            logFunctions.log('Invalid data in body '+str(e))
    

    if (type(get_params) is dict) and (get_params.get('presigned', '') != '1'): # the user wants to upload a file
        return_headers = { 'Content-Type': 'text/html' }
        output = secretsManagement.HTML_uploadForm(get_params['presigned'])

    elif ('type' in jsonbody) and (jsonbody['type'] == "url_verification"):
        output = jsonbody["challenge"]
        # log the request
        logFunctions.log('New challenge replied')
    elif not('token' in slack_event) or not(verificationToken in slack_event['token']):
        output = ''
        logFunctions.log('invalid token')
    elif "bot_id" in slack_event:
        logFunctions.log('Ignoring event from bot')
    elif 'X-Slack-Retry-Num' in event['headers']:
        logFunctions.log('Ignoring a duplicated event')
    elif ("command" in slack_event) and ('/'+settings.botName in slack_event["command"]):
        output = ""
        text = ''
        from_user = ''
        from_team = ''
        from_channel = ''
        from_username = ''
        from_domain = ''
        try:
            if len(slack_event["text"]) > 0:
                text = slack_event["text"][0].strip()
            if len(slack_event["user_id"]) > 0:
                from_user = slack_event["user_id"][0]
            if len(slack_event["team_id"]) > 0:
                from_team = slack_event["team_id"][0]
            if len(slack_event["channel_id"]) > 0:
                from_channel = slack_event["channel_id"][0]
            #response_url = slack_event["response_url"][0]
            if len(slack_event["user_name"]) > 0:
                from_username = slack_event["user_name"][0]
            if len(slack_event["team_domain"]) > 0:
                from_domain = slack_event["team_domain"][0]
            from_user = from_username+'@'+from_domain

            # check for commands

            # get help
            if text.lower() == "help":
                output = settings.help_message

            # get the extended secrets list
            elif text == "??":
                output = secretsManagement.get_secret_list_extended(from_team, from_channel)
            # get the secrets list
            elif text == "?":
                output = secretsManagement.get_secret_list(from_team, from_channel)

            elif text.lower() == "who am i?":
                output = 'id: '+ slack_event['user_id'] + ' team domain: '+ slack_event['team_domain']
                
            # create a new secret
            elif '=' in text:
                newSecretName, newSecretValue = '', ''
                values = text.strip().split(sep='=', maxsplit=1)
                newSecretName = values[0]
                if len(values) > 1:
                    newSecretValue = values[1].strip()
                if bool(newSecretName): # the name is not empty
                    if newSecretName in settings.reservedWords:
                        output = "Sorry, '"+newSecretName+"' is a reserverd word."
                    else:
                        if bool(newSecretValue.strip()): # the secret is not empty
                            old_secret_value = secretsManagement.aws_secretsmanager_get_secret( from_team+'.'+from_channel+'.'+newSecretName.strip() )
                            if len(old_secret_value) > 0: # if exists, update it
                                output = secretsManagement.update_secret(from_user, from_team, from_channel, newSecretName.strip(), newSecretValue, old_secret_value )
                            else: # create a new secret
                                output = secretsManagement.set_secret(from_user, from_team, from_channel, newSecretName.strip(), newSecretValue )
                        else: # if empty, just delete it
                            output = secretsManagement.delete_secret(from_user, from_team, from_channel, newSecretName.strip())
                else:
                    output = "Your secret needs a name"

            # get a secret value
            else:
                SecretName = text.strip()
                output = secretsManagement.get_secret(from_user, from_team, from_channel, SecretName)


        except Exception as e:
            logFunctions.log("Error or missing paramter from slack. "+str(e))
            logFunctions.log(slack_event)


    return {
        'statusCode': 200,
        'body': output,
        'headers': return_headers,
        'isBase64Encoded': isBase64Encoded
    }

if __name__ == '__main__':
    print('running local')
