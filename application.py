import os
import eventlet
import json

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# Globally initialise path - not sure needed
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

# Global variable for channels
channels = []

@app.route("/get_channels", methods = ["GET", "POST"])
def get_channels():

  return json.dumps(channels)

@app.route("/chat", methods=["GET", "POST"])
def chat():
  
  if request.method == "POST":
    new_channel = request.form.get("new_channel_name")
    print("THIS IS THE CHANNEL")
    print(new_channel)
    channels.append(new_channel)
  print("THESE ARE THE CHANNELS")
  print(channels)

  return render_template("chat.html", channels = channels)

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
