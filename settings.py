##################################################
#                                                #
# ############################################## #
# ################## SETTINGS ################## #
# ############################################## #
#                                                #
##################################################

botName = 'sminion'
botVersion = 'v1.05'
region = "eu-west-1"

##################################################
#                                                #
# You shouldn't change anthing beyond this line  #
#                                                #
##################################################

reservedWords = ("help", "?", "??")
S3_content_type = 'application/octet-stream'

help_message = '''
▀▀ *Security Minion {version}. Secrets Manager for Slack.* ▀▀

Usage:

*/{name} help*
> Returns this message
*/{name} ?*
> Returns a list of secrets stored for this channel
*/{name} ??*
> Returns a detailed list of secrets stored for this channel
*/{name} _secret-name_*
> Returns the stored secret
*/{name} _secret-name_=_secret-value_*
> Saves or updates a secret-value as secret-name
*/{name} _secret-name.txt_=+*
> Saves or updates a file as secret-name.txt
*/{name} _secret-name_=*
> Forgets a secret

* Secret names and values are case sensitive.
'''.format(name=botName, version=botVersion)