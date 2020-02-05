import os
import eventlet

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Global variable for channel
channel = None
# Globally initialise path - not sure needed
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@socketio.on("send") # "send" is event to be broadcasted & defined in client-side emit() (1st argument)
def send(data): # data should include channel & message (2nd argument in {})
  # get channel-string for already formatted as "/...io"
  channel = data["channel"]
  # set socketio-path variable to channel-string
  socketio.path = channel
  # get message-string from data
  message = data["message"]
  emit(message, broadcast=True)

if __name__ == '__main__':
  socketio.run(app, debug=True)
