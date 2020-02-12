// get name, if none, redirect to index.html
display_name = localStorage.getItem('display_name');
if (display_name == null) {
  window.location.assign('/');
}

// standard function for creating separate request objects and call this for each AJAX task
// https://stackoverflow.com/questions/11502244/reuse-xmlhttprequest-object-or-create-a-new-one
function newXHR() {
    return new XMLHttpRequest(); // only for standard-compliant browsers
    // would need ActiveXObject for IE? https://stackoverflow.com/questions/11502244/reuse-xmlhttprequest-object-or-create-a-new-one
}

document.addEventListener('DOMContentLoaded', () => {
  // display display_name in top right corner
  var sid = "";
  document.querySelector('#display_name').innerHTML = display_name;
  var socket = io();
  // --------------------------------
  socket.on('connect', function () {
    sid = socket.id;
    console.log(`SID is: ${sid} AND THIS SHOULD ONLY EVER APPEAR ONCE AND NEVER CHANGE`);

    });
  // ----------------------------------

  // IF USER SWITCHES / SELECTS EXISTING CHANNEL
  document.querySelector('#select_channel').onsubmit = () => {
    var channel = document.querySelector('select').value;
    console.log(`CHANNEL SELECTED: ${channel}`);
    // Tell server which channel selected
    const r2 = newXHR();
    r2.open('POST', '/select_channel');
    const data = new FormData();
    data.append('channel', channel);
    console.log(`SENDING SWITCH TO ${channel} TO SERVER`);
    r2.onload = () => {
      //const response = JSON.parse(r2.responseText); - DON@T NEED RESPONSE TEXT HERE DO I?
      //console.log(`JSON RESPONSE TO CHANNEL EXISTS? ${JSON.parse(r1.responseText)}`);
      //----------------------------------
      if (localStorage.getItem('channel') != null)
        {
          socket.emit('leave', {'room': localStorage.getItem('channel'), 'username': display_name, 'sid': sid});
          console.log(`LEAVING ROOM? ${localStorage.getItem('channel')}`); // guess stays connected just room switch?
          console.log(`SID IS NOW: ${sid}`);
        }

      socket.emit('join', {'room': channel, 'username': display_name, 'sid': sid});
      console.log(`AND NOW SID IS: ${sid}`);

      localStorage.setItem('channel', channel);
      const data = new FormData();
      data.append('username', display_name);
      data.append('room', channel);
      data.append('sid', sid);

      console.log(`CONNECTED TO ROOM:${localStorage.getItem('channel')}`); // this not working
      // empty input field (reset form)
      console.log(`SOCKET CONNECTED: ${socket.connected}`);
      document.querySelector('#current_channel').innerHTML = channel;

      //------------------------------------
    };
    r2.send(data);
    document.getElementById('select_channel').reset();
    return false; // here necessary?
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
        alert("Channel already exists"); // this always gets called & then goes on to else
        return false;
      }
      else {
        // create new HTML item for channel list & append
        const option = document.createElement('option');
        option.innerHTML = new_channel_name;
        document.querySelector('select').append(option);

        // connect to websocket and tell Socket.IO client to connect to chosen channel name
        //--------------------------------
        if (localStorage.getItem('channel') != null)
          {
            socket.emit('leave', {'room': localStorage.getItem('channel'), 'username': display_name, 'sid': sid});
            console.log(`LEAVING ROOM? ${localStorage.getItem('channel')}`); // guess stays connected just room switch?
            console.log(`SID IS NOW: ${sid}`);
          }

        socket.emit('join', {'room': new_channel_name, 'username': display_name, 'sid': sid});
        console.log(`AND NOW, WITH NEW CHANNEL, SID IS: ${sid}`);
        localStorage.setItem('channel', new_channel_name);
        const data = new FormData();
        data.append('username', display_name);
        data.append('room', new_channel_name);
        data.append('sid', sid);

        console.log(`CONNECTED TO ROOM:${localStorage.getItem('channel')}`); // this not working
        // empty input field (reset form)
        console.log(`SOCKET CONNECTED: ${socket.connected}`);
        document.querySelector('#current_channel').innerHTML = new_channel_name;
        //----------------------------
        document.getElementById('new_channel').reset();
      }
    };
    r1.send(data);
    return false;
  };

//-------------------
  // broadcast sent message NONE OF THE BELOW WORKS (havent emitted!), ALSO ENSURE MSG FIELD ONLY CLEAR WHEN CONNECTED TO CHANNEL
  document.querySelector('#send_message').onsubmit = () => {
    var message = document.querySelector('#message').value;
    console.log(`MESSAGE IS ${message}`);
    console.log(`ROOM is ${localStorage.getItem('channel')}`);
    // so far above this works
    socket.emit('send', {'message': message, 'room': localStorage.getItem('channel')}); // need sender,. butnot channel.. , too?
    console.log(`SENDING ${message} ONCE OR MORE?`); // only once
    return false;
  }

  socket.on('broadcast message', function handle_broadcast (data) {
    console.log(data);


    const div = document.createElement('div');
    const p = document.createElement('p');
    const span = document.createElement('span');
    p.innerHTML = data.message;
    var today = new Date();
    var time = today.getHours() + ":" + today.getMinutes();
    span.innerHTML = time;
    span.setAttribute('class', 'time-left');
    div.appendChild(p);
    div.appendChild(span);
    div.setAttribute('class', 'container');
    document.querySelector('#chat_window').append(div);
    document.getElementById('message').value = "";
    return false;

  });

//-----------------


});
