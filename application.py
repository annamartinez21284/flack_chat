import os
import eventlet
import json

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from tempfile import mkdtemp
from flask_socketio import SocketIO, emit, Namespace

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp() # temp storage? defaults to flask_session in current working dir
app.config["SESSION_PERMANENT"] = False #default to true, use perm sess, why false?
app.config["SESSION_TYPE"] = "filesystem"  #defaults to null
Session(app) #creates Session-object by passing it the application

# Globally initialise path - not sure needed
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Global variable for channels, current namespace and
channels = []
messagetext = None


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_channel", methods=["GET", "POST"])
def select_channel():
  if request.method == "POST": # check later if this necessary
    channel = request.form.get("channel") # "channel" here needs to refer to what data.append() calls it!! not to HTML tag names!!
    print("SERVER SWITCHING TO CHANNEL: "+channel)
    print("LEAVING NAMESPACE: "+session["namespace"])
    session["namespace"] = "/"+channel
    print(session["namespace"])


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
      session["namespace"] = "/"+new_channel
      print("ADDING NEW CHANNEL: "+session["namespace"])
      return json.dumps(channels)

  return render_template("chat.html", channels = channels)


@socketio.on("send", namespace = '/est') # "send" is event to be broadcasted & defined in client-side emit() (1st argument)
def handle_send(data): # data should include message, sender name, time? - make an object? (2nd argument in {})
  messagetext = data["message"]
  print("THE MESSAGE IS :"+messagetext)
  print("THE NAMESPACE IS: "+namespace)
  emit("broadcast message", {"message": messagetext}, broadcast = True)


if __name__ == '__main__':
  socketio.run(app, debug=True)
