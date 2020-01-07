#
# Slack Functions
#

import os
from slack.web.client import WebClient as SlackClient

def escape(t): # Reserved for future use
    # After testing, there was no need to escape the user input, so I disabled it.
    # per Slack documentation, only need to escape &, < and >. https://api.slack.com/reference/surfaces/formatting
    #return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return t

def get_channel_info(channel1, verbose = False):
    try:
        botToken = os.environ.get('BotUserOAuthAccessToken')
        slack_client = SlackClient(botToken)
        info = slack_client.conversations_info( channel=channel1 )
        if info['ok']:
            if info['channel']['is_private']:
                if verbose:
                    return 'this is a *private channel*'
                else:
                    return ''
            else:
                return '\nWARNING: this is a *public channel*'
        else:
            return '\nWARNING: I can not check if this channel is private'
    except Exception as e:
        if verbose:
            return '\nWARNING. I can not check if this channel is private! '+str(e)
        else:
            return '\nWARNING. I can not check if this channel is private! '

