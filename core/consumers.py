# In consumers.py
import logging
from django.conf import settings
from channels import Group
from channels import Channel
from channels.sessions import channel_session, enforce_ordering

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Connected to websocket.connect
@enforce_ordering(slight=True)
@channel_session
def ws_connect(message):
    # Work out game name from path (ignore slashes)
    game = message.content['path'].strip("/")
    session_id = message.channel_session.session_key
    reply_channel = message.reply_channel

    #log name of game
    logger.info('path: ' + message.content['path'])
    logger.info('game name: ' + game)

    # Save game in session and add us to the group
    message.channel_session['game'] = game
    Group("chat-%s" % game).add(message.reply_channel)

    settings.MATCH_MAKING_MAP.append({'session': session_id,
                                      'game': game,
                                      'reply_channel': reply_channel})

    reply_channel.send({'text': 'You have joined the queue for ' + game})

    # TODO: whenever a user connects, check if we have 2 users to start a given game
    # TODO: if so send both a message and remove them from queue
    # TODO: else do nothing

# Connected to websocket.receive
@enforce_ordering(slight=True)
@channel_session
def ws_message(message):

    # TODO: if it's polling message, check if the user is already in queue
    # TODO: if so, check if we have 2 users to start a given game
    # TODO: if so send both a message and remove them from queue
    # TODO: else do nothing

    Group("chat-%s" % message.channel_session['game']).send({
        "text": message['text'],
    })

# Connected to websocket.disconnect
@enforce_ordering(slight=True)
@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['game']).discard(message.reply_channel)

    # re-directed or disconnected / channel closed - remove user from matchmaking queue
    session_id = message.channel_session.session_key
    reply_channel = message.reply_channel
    settings.MATCH_MAKING_MAP.remove({'session': session_id,
                                      'game': message.channel_session['game'],
                                      'reply_channel': reply_channel})