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
  def __init__(self, sender, text, time, id):

    self.sender = sender
    self.text = text
    self.time = time
    self.id = id

# Globally initialise path
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Set of channel objects
channels = set()
# Set of strings containing channel object names
channelnames = set()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_channel", methods=["GET", "POST"])
def select_channel():
  channel = request.form.get("channel")
  # get Channel object c with selected name 'channel'
  c = next((c for c in channels if c.name == channel), None)
  if (c):
    print("SERVER SWITCHING TO CHANNEL: ")
    print(c.name)
    session["channel"] = channel
    #return jsonify({"success": True})
  return render_template("chat.html", channels = channelnames)

@app.route("/new_channel", methods=["GET", "POST"])
def new_channel():
  # get channel name from user input
  new_channel = request.form.get("new_channel_name")
  # create new channel object & initialise message_log list
  c = Channel(name = new_channel, message_log = [])
  if new_channel in channelnames:
    return jsonify({"channel_exists": True})

  # if channel doesn't exist, add to set of channels and store channel name in session
  else:
    channelnames.add(c.name)
    channels.add(c)
    session["channel"] = c.name
    return json.dumps(list(channelnames))

  return render_template("chat.html", channels = channelnames)

@app.route("/delete_message", methods=["GET", "POST"]) # this needs to get passed message details here
def delete_message():
  id = request.form.get("msg_id")
  # with this id, find the message and delete in Channel's log
  print("ID IS")
  print(id)
  c = next((c for c in channels if c.name == session["channel"]), None)
  print("CHannel found is:")
  print(session["channel"])
  print(c.message_log) # well this does print out message objects
  for m in c.message_log:
    print(f"M.ID is: {m.id}") #gets done
    if (int(m.id) == int(id)):
      print(f"DELETING {m.text} with ID: {m.id}")
      i = int(id) -1
      del c.message_log[i]
      return jsonify({"success": True})
  return jsonify({"success": True})


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    sid = data['sid']
    session["channel"] = room
    # find channel object thru its name-attribute provided by user (as room) and store in variable c
    c = next((c for c in channels if c.name == room), None)
    join_room(room, sid=sid)
    # create and use list to emit log to client as JSON (list is serializable type)
    message_list = []
    if (c):
      for message in c.message_log:
        print(f"PRINITING MESSAGE: {message}") # object...<__main etc
        m_dict = message.__dict__
        message_list.append(m_dict)
    emit("display_messages", json.loads(json.dumps(message_list)), room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    sid = data['sid']
    leave_room(room, sid=sid)
    send(username + ' has left the room.', room=room)

@socketio.on('send')
def handle_send(data):
  # get Channel object c with current channel
  room = data["room"]
  c = next((x for x in channels if x.name == room), None)
  # when message received from client, create new Message object with data
  m = Message(sender=data["sender"], text = data["message"], time = data["time"], id = len(c.message_log) + 1)
  c.add_message(m)
  # this stuff here in this format is so Handlebars can read 'data' in the end
  m_dict = m.__dict__
  message_list = []
  message_list.append(m_dict)

  emit("broadcast message", json.loads(json.dumps(message_list)), room=room)

#@socketio.on('delete')
#def on_delete(data):
#  pass


if __name__ == '__main__':
  socketio.run(app, debug=True)
