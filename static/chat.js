document.addEventListener('DOMContentLoaded', () => {

        document.querySelector('#display_name').innerHTML = localStorage.getItem('display_name');

        // IF USER ALREADY IS ON CHANNEL

        // IF USER SWITCHES / SELECTS EXISTING CHANNEL

        // IF USER CREATES NEW CHANNEL
        document.querySelector('#new_channel').onsubmit = () => {
          // stop browser default behaviour (submission of form to server), but NOT propagation to DOM (return false; would)
          //e.preventDefault(); - using return false below instead - seems to make no difference
          // get new Channel name
          const new_channel_name = document.querySelector('#new_channel_name').value;
          console.log(`New channel name: ${new_channel_name}`);



          // STEP1: get channel list from server - PROB BETTER ALL SERVER-SIDE SINCE LIST NEEDS FETCHING FROM IT ANYWAY
          const request2 = new XMLHttpRequest();
          request2.open('GET', '/get_channels');
          // callback function: when request completed,
          request2.onload = () => {
            // extract list in JSON format from request (returned by get_channels() in application.py)
            const response = JSON.parse(request2.responseText);
            console.log(`RESPONSE FROM SERVER IS: ${response}`);
            // look for channel in returned array
            if (response.find(function(element) {return element == new_channel_name;}))
                {

              // empty input field (reset form)
              document.getElementById('new_channel').reset();
              // check with server if channel name already exists (AJAX request)
              alert("Channel already exists"); // this always gets called & then goes on to else

              return false;
              }
            else {
              // send new channel name to server
              const request1 = new XMLHttpRequest(); // DO I NEED 2 request objects?
              request1.open('POST', '/chat');
              const data = new FormData();
              data.append('new_channel_name', new_channel_name);
              console.log(`SENDING ${new_channel_name} TO SERVER`);
              request1.send(data);
              // create new HTML item for channel list & append
              const option = document.createElement('option');
              option.innerHTML = new_channel_name;
              document.querySelector('select').append(option);

              var socket = io(`/${new_channel_name}`);
              socket.on('connect', () => {
                console.log(`CONNECTED TO NAMESPACE:${socket.nsp}`); // or .nsp.name
                console.log(`SOCKET CONNECTED = ${socket.connected}`);

              });
              // empty input field (reset form)
              document.getElementById('new_channel').reset();
            }
          };
          request2.send();



          // save channel on server
          //const request3 = new XMLHttpRequest();
          //request3.open('POST', '/chat');
          //request3.send(new_channel_name); // this isnt being sent





          // connect to websocket and tell Socket.IO client to connect to chosen channel name (path)
          //var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port,  {'path': `/${new_channel_name}.io` });// is here the right place where i initialise path url?
          //var socket = io.of('new_channel_name'); // this is server-side code??
          //var socket = io(`/${new_channel_name}`);
          //var socket = io();
          //var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
          // once, connected, do...

          return false;
          };
      });
