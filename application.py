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
#  def add_participant(self, participant):
#    self.participants.add(participant)

#  def remove_participant(self, participant):
#    participants = [p for p in participants if p != participant]
  def add_message(self, message):
    self.message_log.append(message)
    if len(self.message_log) > 100:
      del self.message_log[0]

  def __init__(self, name, message_log):
    self.name = name
    #self.participants = participants
    self.message_log = message_log

class Message: # CREATE ONE OF THEM EACH TIME ...
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
#    participant = request.form.get("participant")
    # get Channel object c with selected name 'channel'
    c = next((c for c in channels if c.name == channel), None)
    if (c):
  #    c.add_participant(participant)
      print("SERVER SWITCHING TO CHANNEL: ")
      print(c.name)
      session["channel"] = channel # somehow this needs to be in on_join instead - can delete here?

      return jsonify({"success": True})# gotta be json or template or nothing else?

  return render_template("chat.html", channels = channelnames) # message=messages (from Object and then for message in messages jinja syntx in html)
                                                        # has to come from the server anyway

@app.route("/new_channel", methods=["GET", "POST"])
def new_channel():
  if request.method == "POST":  # check later if this necessary
    new_channel = request.form.get("new_channel_name")
#    participant = request.form.get("participant")
#    print("I GOT THE PARTICIPANT" + participant)
    c = Channel(name = new_channel, message_log = [])
#    c.add_participant(participant)
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
    print(f"JOINING channel below on SID: ") #request.sid not a thing
    print(request.sid)

    message_list = []
    for message in c.message_log:
      m_dict = message.__dict__
      message_list.append(m_dict)

    print("IN ON_JOIN, THE CHANNEL IS: "+session["channel"]+ " = " + room + "="+c.name+"JUST TO CHECK")
    #send(username + ' has entered the room.', room=room)
    emit("display_messages", json.loads(json.dumps(message_list)), room=room) # 2nd argument a tuple if I want >1. maybe dict of messages?

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
  m = Message(sender=data["sender"], text = data["message"], time = data["time"])
  room = data["room"]

  # get Channel object c with current channel
  c = next((x for x in channels if x.name == room), None)
  c.add_message(m)

  print("THE MESSAGE IS :"+m.text)
  print("THE CHANNEL IS: "+session["channel"]+ " = " + room + "="+c.name+"JUST TO CHECK")
  # call Object MessageLog's method add to add message and trim log
  emit("broadcast message", {"message": m.text, "sender": m.sender}, room=room)


if __name__ == '__main__':
  socketio.run(app, debug=True)
