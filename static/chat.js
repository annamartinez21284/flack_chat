document.addEventListener('DOMContentLoaded', () => {

        document.querySelector('#display_name').innerHTML = localStorage.getItem('display_name');

        // IF USER ALREADY IS ON CHANNEL

        // IF USER SELECTS EXISTING CHANNEL

        // IF USER CREATES NEW CHANNEL
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
        socket.on('connect', () => {
          console.log(`Connected to SOCKET ID: ${socket.id}`);
            });
        // WHY CAN'T THE ABOVE 4 LINES NOT BE INSIDE .... .onsubmit? ASK...
        document.querySelector('#new_channel').onsubmit = () => {
          // get new Channel name
          const new_channel_name = document.querySelector('#new_channel_name').value;
          console.log(`New channel name: ${new_channel_name}`);

          // check if channel name already extsis
          // connect to websocket and tell Socket.IO client to connect to chosen channel name (path)
          //var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port,  {'path': `/${new_channel_name}.io` });// is here the right place where i initialise path url?
          //var socket = io.of('new_channel_name');

          //var socket = io('/my-namespace');
          //var socket = io();

          // once, connected, do...
          socket.on('connect', () => {
            console.log("THIS NEVER GETS EXECUTED");
          }); return false;

          };
      });
