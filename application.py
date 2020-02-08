import os
import eventlet
import json

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, Namespace

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# Globally initialise path - not sure needed
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

# Global variable for channels
channels = []
namespace = None;
messagetext = None;

@app.route("/select_channel", methods=["GET", "POST"])
def select_channel():
  if request.method == "POST": # check later if this necessary
    channel = request.form.get("channel") # "channel" here needs to refer to what data.append() calls it!! not to HTML tag names!!
    print("SERVER SWITCHING TO CHANNEL:")
    print(channel)
    return jsonify({"success": True})# gotta be json or template or nothing else?

  return render_template("chat.html", channels = channels)

@app.route("/new_channel", methods=["GET", "POST"])
def new_channel():
  if request.method == "POST":  # check later if this necessary
    new_channel = request.form.get("new_channel_name")
    print("THIS IS THE RECEIVED NEW CHANNEL")
    print(new_channel)
    print("THESE ARE THE CHANNELS")
    print(channels)
    if new_channel in channels:
      return jsonify({"channel_exists": True})

    else:
      print("ADDING NEW CHANNEL:")
      print(new_channel)
      channels.append(new_channel)
      namespace = new_channel;
      return json.dumps(channels)

  return render_template("chat.html", channels = channels)


socketio.on_event('send', 'handle_send', namespace = namespace)
@socketio.on("send") # "send" is event to be broadcasted & defined in client-side emit() (1st argument)
def handle_send(data): # data should include channel & message (2nd argument in {})
  messagetext = data["message"]
  print("THE MESSAGE IS:")
  print(messagetext)
  namespace = data["namespace"]
  print("THE NAMESPACE IS:")
  print(messagetext)
  emit("broadcast message", {"message": messagetext}, broadcast=True)


  # get channel-string for already formatted as "/...io"
  #channel = data["channel"]
  # set socketio-path variable to channel-string
  #socketio.path = channel
  # get message-string from data


if __name__ == '__main__':
  socketio.run(app, debug=True)
