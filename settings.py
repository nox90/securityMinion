##################################################
#                                                #
# ############################################## #
# ################## SETTINGS ################## #
# ############################################## #
#                                                #
##################################################

botName = 'sminion'
botVersion = 'v1.06'
region = "eu-west-1"
check_private_channel = False

##################################################
#                                                #
# You shouldn't change anthing beyond this line  #
#                                                #
##################################################

reservedWords = ("help", "info", "delete", "file", "?", "??")
S3_content_type = 'application/octet-stream'

help_message = '''
▀▀ *Security Minion {version}. Secrets Manager for Slack.* ▀▀
​
Usage:
​
> *List all* secrets stored for this channel (?? for extra info):
/{name} `?`
/{name} `??`
> *Return* a stored secret:
/{name} `secret-name`
> *Save* or *update* a secret-value as secret-name:
/{name} `secret-name`=`secret-value`
> Save or update a *file* as secret-name.txt:
/{name} file `secret-name.txt`
> *Forget* a stored secret:
/{name} delete `secret-name`
> *Help* (this message):
/{name} `help`
​
_Secret names and values are case sensitive._
'''.format(name=botName, version=botVersion)