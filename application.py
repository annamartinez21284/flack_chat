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

class Channel:
  def add_message(self, message):
    self.message_log.append(message)
    if len(self.message_log) > 100:
      del self.message_log[0]

  def __init__(self, name, message_log):
    self.name = name
    self.message_log = message_log

class Message:
  def __init__(self, sender, text, time):
    self.sender = sender
    self.text = text
    self.time = time

# Globally initialise path - not sure needed
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Global variables
channels = set()
channelnames = set()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_channel", methods=["GET", "POST"])
def select_channel():
  if request.method == "POST": # check later if this necessary
    channel = request.form.get("channel") # "channel" here needs to refer to what data.append() calls it!! not to HTML tag names!!
    # get Channel object c with selected name 'channel'
    c = next((c for c in channels if c.name == channel), None)
    if (c):
      print("SERVER SWITCHING TO CHANNEL: ")
      print(c.name)
      session["channel"] = channel # somehow this needs to be in on_join instead - can delete here?
      return jsonify({"success": True})# gotta be json or template or nothing else?

  return render_template("chat.html", channels = channelnames)

@app.route("/new_channel", methods=["GET", "POST"])
def new_channel():
  if request.method == "POST":  # check later if this necessary
    new_channel = request.form.get("new_channel_name")
    c = Channel(name = new_channel, message_log = [])
    print("THIS IS THE RECEIVED NEW CHANNEL: "+c.name) #later just c and below iterate over names
    print(f"THESE ARE THE CHANNELS: {channelnames}")

    if new_channel in channelnames:
      return jsonify({"channel_exists": True})

    else:
      channelnames.add(c.name)
      channels.add(c)
      session["channel"] = c.name
      print("ADDING NEW CHANNEL: "+session["channel"])
      return json.dumps(list(channelnames))

  return render_template("chat.html", channels = channelnames)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    sid = data['sid']
    session["channel"] = room
    c = next((c for c in channels if c.name == room), None)
    join_room(room, sid=sid)
    print(f"ELVIS HAS ENTERED {room} OR {c.name} AS {username}")
    message_list = []
    for message in c.message_log:
      m_dict = message.__dict__
      message_list.append(m_dict)

    print("IN ON_JOIN, THE CHANNEL IS: "+session["channel"]+ " = " + room + "="+c.name+"JUST TO CHECK")

    emit("display_messages", json.loads(json.dumps(message_list)), room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    sid = data['sid']
    leave_room(room, sid=sid)
    print(f"ELVIS HAS LEFT {room} AS {username}")
    send(username + ' has left the room.', room=room)

@socketio.on("send")
def handle_send(data):
  m = Message(sender=data["sender"], text = data["message"], time = data["time"])
  room = data["room"]

  # get Channel object c with current channel
  c = next((x for x in channels if x.name == room), None)
  c.add_message(m)

  print("THE MESSAGE IS :"+m.text)
  print("THE CHANNEL IS: "+session["channel"]+ " = " + room + "="+c.name+"JUST TO CHECK")

  emit("broadcast message", {"message": m.text, "sender": m.sender, "time": m.time}, room=room)


if __name__ == '__main__':
  socketio.run(app, debug=True)
