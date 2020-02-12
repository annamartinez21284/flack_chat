import os
import eventlet
import json

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from tempfile import mkdtemp
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp() # temp storage? defaults to flask_session in current working dir
app.config["SESSION_PERMANENT"] = False #default to true, use perm sess, why false?
app.config["SESSION_TYPE"] = "filesystem"  #defaults to null
Session(app) #creates Session-object by passing it the application

# Globally initialise path - not sure needed
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Global variable for channels
channels = []
messagetext = None


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_channel", methods=["GET", "POST"])
def select_channel():
  if request.method == "POST": # check later if this necessary
    channel = request.form.get("channel") # "channel" here needs to refer to what data.append() calls it!! not to HTML tag names!!
    print("SERVER SWITCHING TO CHANNEL: ")
    print(channel)
    print("LEAVING CHANNEL: ")
    #print(session["channel"])
    session["channel"] = channel

    return jsonify({"success": True})# gotta be json or template or nothing else?

  return render_template("chat.html", channels = channels)

@app.route("/new_channel", methods=["GET", "POST"])
def new_channel():
  if request.method == "POST":  # check later if this necessary
    new_channel = request.form.get("new_channel_name")
    print("THIS IS THE RECEIVED NEW CHANNEL: "+new_channel)
    print(f"THESE ARE THE CHANNELS: {channels}")

    if new_channel in channels:
      return jsonify({"channel_exists": True})

    else:
      channels.append(new_channel)
      session["channel"] = new_channel
      print("ADDING NEW CHANNEL: "+session["channel"])
      return json.dumps(channels)

  return render_template("chat.html", channels = channels)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    sid = data['sid']

    join_room(room, sid=sid)
    print(f"ELVIS HAS ENTERED {room} AS {username}")
    print(f"JOINING channel below on SID: ") #request.sid not a thing
    print(request.sid)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    sid = data['sid']
    leave_room(room, sid=sid) # sid = ...
    print(f"ELVIS HAS LEFT {room} AS {username}")
    send(username + ' has left the room.', room=room)

@socketio.on("send") # "send" is event to be broadcasted & defined in client-side emit() (1st argument)
def handle_send(data): # data should include message, sender name, time? - make an object? (2nd argument in {})
  messagetext = data["message"]
  room = data["room"]
  print("THE MESSAGE IS :"+messagetext)
  print("THE CHANNEL IS: "+session["channel"])
  emit("broadcast message", {"message": messagetext}, room=room) #or data["message" as 2nd arg]


if __name__ == '__main__':
  socketio.run(app, debug=True)
