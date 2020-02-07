display_name = localStorage.getItem('display_name');
if (display_name == null) {
  window.location.assign('/');
}

function newXHR() {
    return new XMLHttpRequest(); // only for standard-compliant browsers
    // would need ActiveXObject for IE? https://stackoverflow.com/questions/11502244/reuse-xmlhttprequest-object-or-create-a-new-one
}

document.addEventListener('DOMContentLoaded', () => {

  document.querySelector('#display_name').innerHTML = display_name;

  // IF USER SWITCHES / SELECTS EXISTING CHANNEL

  // IF USER CREATES NEW CHANNEL
  document.querySelector('#new_channel').onsubmit = () => {
    // stop browser default behaviour (submission of form to server), but NOT propagation to DOM (return false; would)
    //e.preventDefault(); - using return false below instead - seems to make no difference
    // get new Channel name
    const new_channel_name = document.querySelector('#new_channel_name').value;
    console.log(`New channel name: ${new_channel_name}`);

    // Send new channel name to server
    const r1 = newXHR();
    r1.open('POST', '/chat');
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
        //option.innerHTML = new_channel_name;
        document.querySelector('select').append(option);

        // connect to websocket and tell Socket.IO client to connect to chosen channel name
        var socket = io(`/${new_channel_name}`);
        socket.on('connect', () => {
          console.log(`CONNECTED TO NAMESPACE:${socket.nsp}`); // or .nsp.name
          // empty input field (reset form)
          console.log(`SOCKET CONNECTED: ${socket.connected}`);
          document.getElementById('new_channel').reset();
          }
        )
      }
    };
    r1.send(data);
    return false;
  };
});
