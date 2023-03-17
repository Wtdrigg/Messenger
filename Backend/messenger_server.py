"""
To Access this app, run the run then access *server ip address*/messenger in a web browser. IP address will be
displayed in the  terminal along with all HTTP requests received.
"""

from flask import Flask, request
from flask_socketio import SocketIO, join_room
from datetime import datetime

# Creates the Flask App and wraps SocketIO around it.
app = Flask(__name__)
Socketio = SocketIO(app)


# Abstract class, for code organization, not object instantiation
class ChatApp:

    # Constant that determines how many messages will be displayed at one. Messages are First In, First Out.
    STORED_MESSAGE_COUNT = 20

    # Attributes used to keep track of which users are connected, how many, and stored messages
    user_sid_reference = {}
    user_count = 0
    data = []

    # On Get request, reads the main HTML file and sends it to the requester in JSON format.
    @staticmethod
    @app.route('/messenger', methods=['GET'])
    def index():
        with open('Backend/messenger.html') as f:
            response = f.read()
            return response, 200

    # Listens for connections, then increments the user_count amount. 
    @staticmethod
    @Socketio.on('connect')
    def user_connected(user):
        ChatApp.user_count += 1

    # Listens for disconnects, then decrements the user_count amount.
    @staticmethod
    @Socketio.on('disconnect')
    def user_disconnected():
        disconnected_user = ChatApp.user_sid_reference[request.sid]
        current_time = str(datetime.now())
        disconnection_message = {'user': disconnected_user, 'time': current_time, 'message': ':Disconnect'}
        ChatApp.data.append(disconnection_message)
        ChatApp.check_message_overflow()
        ChatApp.broadcast_messages()
        ChatApp.user_count -= 1
        # Clears all saved messages if the last user disconnects.
        if ChatApp.user_count == 0:
            ChatApp.data = []

    # Listens for Join events, announces that the user has joined.
    @staticmethod       
    @Socketio.on('join')
    def join(message_content):
        join_room(message_content['user'])
        ChatApp.data.append(message_content)
        ChatApp.check_message_overflow()
        ChatApp.broadcast_messages()
        ChatApp.user_sid_reference[request.sid] = message_content['user']

    # Listens for user messages, then broadcasts that message to all other connections.
    @staticmethod
    @Socketio.on('submitmessage')
    def submit_message(message_content):
        ChatApp.data.append(message_content)
        ChatApp.check_message_overflow()
        ChatApp.broadcast_messages()

    # Sends an event to tell the frontend to clear all messages.
    @staticmethod
    def clear_messages():
        Socketio.emit('clearmessages', broadcast=True)

    # Sends a broadcast event to all connected users that contains all messages to display.
    @staticmethod
    def broadcast_messages():
        ChatApp.clear_messages()
        for message in ChatApp.data:
            Socketio.emit('serverbroadcast', message, broadcast=True)

    # counts stored messages, removes the oldest if the amount is greater than the STORED_MESSAGE_COUNT constant.
    @staticmethod
    def check_message_overflow():
        if len(ChatApp.data) > ChatApp.STORED_MESSAGE_COUNT:
            for i in range(len(ChatApp.data) - ChatApp.STORED_MESSAGE_COUNT):
                ChatApp.data.pop(0)
        

if __name__ == '__main__':

    # Activates the Server, use host='0.0.0.0' to run on a local network, otherwise this will default to localhost only.
    # IP Address used will be displayed in the terminal.
    with app.app_context():

        Socketio.run(app, host='0.0.0.0')
