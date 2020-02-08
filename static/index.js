// if the user already has a display name, redirect to chat
if (localStorage.getItem('display_name')!= null)
  { window.location.assign('/select_channel');
  localStorage.setItem('display_name');}
  // ... ->then in chat.html set name in the DOM

  // if not, get chosen display_name and set it
else {
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#new').onsubmit = function () {
      const dname = document.querySelector('#display_name').value;
      localStorage.setItem('display_name', dname);
      window.location.replace('/select_channel');
    };

  });
}
