// get name & channel, if none, redirect to index.html
const display_name = localStorage.getItem('display_name');
var current_channel = localStorage.getItem('current_channel');


// redirect user to index if not stored (by display_name)
function loggedin () {
  if (localStorage.getItem('display_name') == null) {
    window.location.assign('/');
  }
}

loggedin();


// standard function for creating separate request objects and call this for each AJAX task
// https://stackoverflow.com/questions/11502244/reuse-xmlhttprequest-object-or-create-a-new-one
function newXHR() {
    return new XMLHttpRequest(); // only for standard-compliant browsers
    // would need ActiveXObject for IE? https://stackoverflow.com/questions/11502244/reuse-xmlhttprequest-object-or-create-a-new-one
}

// timestamp formatting for minutes
function addZero(i) {
  if (i < 10) {
    i = "0" + i;
  }
  return i;
}

// Handlebars JS template for messages in chat window
const template = Handlebars.compile(document.querySelector('#chat_log').innerHTML);


document.addEventListener('DOMContentLoaded', () => {

  document.querySelector('#display_name').innerHTML = display_name;
  const chatWindow = document.querySelector('#chat_window');

  // disable sending messages if no channel selected
  if (current_channel == null || current_channel == undefined)
    {
      document.querySelector('#send_button').disabled = true;
    }

  // connect socket and store socket ID
  var sid = "";
  var socket = io();
  socket.on('connect', function () {
    sid = socket.id;
    console.log(`SID is: ${sid}`);
    });

  // IF USER WAS ALREADY CONNECTED TO CHANNEL, RECONNECT HIM THERE
  function reconnect () {
    if (localStorage.getItem('current_channel') != null && localStorage.getItem('current_channel') != undefined) {
      const r = newXHR();
      r.open('POST', '/select_channel');
      const data = new FormData();
      data.append('channel', current_channel);
      r.onload = () => {
          socket.emit('join', {'room': current_channel, 'username': display_name, 'sid': sid});
          document.querySelector('#current_channel').innerHTML = "Connected to " + current_channel;
      };
      r.send();
      document.querySelector('#send_button').disabled = false;
    }
  }
  reconnect();


  // IF USER SWITCHES / SELECTS EXISTING CHANNEL
  document.querySelector('#select_channel').onsubmit = () => {
    current_channel = document.querySelector('select').value;

    // Tell server which channel selected
    const r2 = newXHR();
    r2.open('POST', '/select_channel');
    r2.onload = () => {
      if (current_channel != null && current_channel != undefined)
        {
          socket.emit('leave', {'room': current_channel, 'username': display_name, 'sid': sid});
          console.log(`LEAVING ROOM ${current_channel} on SID ${sid}`);
        }

      socket.emit('join', {'room': current_channel, 'username': display_name, 'sid': sid});

      localStorage.setItem('current_channel', current_channel);
      console.log(`CONNECTED TO ROOM:${localStorage.getItem('current_channel')}`);
      document.querySelector('#current_channel').innerHTML = "Connected to " + current_channel;
    };
    r2.send();

    document.getElementById('select_channel').reset();
    document.querySelector('#send_button').disabled = false;
    return false;
  }

  // IF USER CREATES NEW CHANNEL
  document.querySelector('#new_channel').onsubmit = () => {
    // stop browser default behaviour (submission of form to server), but NOT propagation to DOM (return false; would)
    //e.preventDefault(); - using return false below instead - seems to make no difference

    // get new Channel name
    const new_channel_name = document.querySelector('#new_channel_name').value;
    console.log(`New channel name: ${new_channel_name}`);

    // Send new channel name to server
    const r1 = newXHR();
    r1.open('POST', '/new_channel');
    const data = new FormData();
    data.append('new_channel_name', new_channel_name);
    console.log(`SENDING ${new_channel_name} TO SERVER`);
    r1.onload = () => {
      const response = JSON.parse(r1.responseText);
      console.log(`JSON RESPONSE TO CHANNEL EXISTS? ${JSON.parse(r1.responseText)}`);
      if (response.channel_exists) {
        // empty input field (reset form)
        document.getElementById('new_channel').reset();
        // check with server if channel name already exists (AJAX request)
        alert("Channel already exists");
        return false;
      }
      else {
        // create new HTML item for channel list & append
        const option = document.createElement('option');
        option.innerHTML = new_channel_name;
        document.querySelector('select').append(option);

        // connect to websocket and tell Socket.IO client to connect to chosen channel name
        if (current_channel != null && current_channel != undefined)
          {
            socket.emit('leave', {'room': current_channel, 'username': display_name, 'sid': sid});
            console.log(`LEAVING ROOM: ${current_channel}, SID IS: ${sid}`);
          }

        socket.emit('join', {'room': new_channel_name, 'username': display_name, 'sid': sid});
        current_channel = new_channel_name;
        localStorage.setItem('current_channel', current_channel);

        const data = new FormData();
        data.append('username', display_name);
        data.append('room', new_channel_name);
        data.append('sid', sid);

        console.log(`CONNECTED TO ROOM:${current_channel}`);
        // empty input field (reset form)
        document.querySelector('#current_channel').innerHTML = "Connected to " + new_channel_name;
        document.getElementById('new_channel').reset();
      }
    };
    r1.send(data);
    document.querySelector('#send_button').disabled = false;

    return false;
  };

  // Allow Enter key to submit message
  var message = document.getElementById("message");
  message.addEventListener("keyup", (e) => {
    if (e.keyCode === 13)
    {e.preventDefault();
    document.getElementById("send_button").click();}
  });

  // broadcast sent message
  document.querySelector('#send_message').onsubmit = () => {
    var message = document.querySelector('#message').value;
    var today = new Date();
    var time = today.getHours() + ":" + addZero(today.getMinutes());
    var sender = display_name;
    socket.emit('send', {'message': message, 'time': time, 'sender': sender, 'room': current_channel});
    return false;
  }

  // display message_log upon connection to channel
  socket.on('display_messages', function handle_messagelog (data) {
    chatWindow.innerHTML = "";
    // populate JS template (Handelbars) with data (message log)
    const element = template({'values': data});
    chatWindow.innerHTML += element;

    // have scrollbar always at the bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;

  });

 // broadcast sent message to all connected clients
  socket.on('broadcast message', function handle_broadcast (data) {

    const element = template({'values': data});
    chatWindow.innerHTML += element;

    chatWindow.scrollTop = chatWindow.scrollHeight;
    document.getElementById('message').value = "";
  });

  // DELETE MESSAGE
  // Event delegation - live saving!!!!!!!!
  chatWindow.addEventListener("click", function (e) {
    e.preventDefault();
    // e.target is the clicked element!!
    if (e.target.classList.contains("delete_message")) // THIS DOESN'T PICK UP, OK SOMETIMES IT DOES
      {
        const span = e.target.parentElement;
        const div = span.parentElement;
        const sender = div.firstChild.nextSibling;

        console.log(`SENDER IS: ${sender.innerHTML.trim()}`);
        console.log(`DISPLAY_NAME IS ${display_name}`);
        if (sender.innerHTML.trim() != display_name) {
          alert("You can only delete own messages.");
          return false;
        }
        else {
          console.log(`DELETING ${div.firstChild.nextSibling.nextSibling.innerHTML}`);
          // below no longer needed as onload will instantly remove from view
          //var str = "<i>MESSAGE DELETED</i>";
          var msg = sender.nextSibling.nextSibling;
          //msg.innerHTML = str;
          // DO SERVER STUFF
          const r3 = newXHR();
          r3.open('POST', '/delete_message');
          const data = new FormData();
          var msg_id = msg.nextSibling.innerHTML;
          console.log(`MESSAGE ID TO DELETE: ${msg_id}`);
          data.append('msg_id', msg_id);
          r3.onload = () => {
            // reload all messages without deleted ones - aka re-join room to broadcast
            socket.emit('join', {'room': current_channel, 'username': display_name, 'sid': sid});
          }
          r3.send(data);
        }
      }
    });


  // exit chat app by clearing display_names
  document.querySelector('#exit_button').onclick = () => {
    localStorage.clear();
    loggedin();
  }

});
