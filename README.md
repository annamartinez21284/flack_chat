# Project 2

Web Programming with Python and JavaScript

## Description

This is a simple **multi-channel chat application** using JavaScript, Socket.IO and Python packages Flask and Flask-SocketIO.
It is my submission of Project 2 of CS50W. Full details of usage/requirements at:
https://docs.cs50.net/web/2019/x/projects/2/project2.html.

In addition to those, there is the option to delete one's own messages.

The files used are:
* application.py - contains Python server-side logic
* chat.js - contains most of client-side JS (chat page)
* index.js - contains JS for index.html (sign-in page)
* chat.html - sign-in page
* index.html - chat page
* layout.html - layout for index.html
* styles.css - stylesheet

## Usage

Instead of setting & exporting flask app, run:

```
python3 application.py
```

The way to test it that worked best for me, (because of how Chrome works, I presume), is to have one normal and one incognito window.


## Limitations

* As per assignment, no database used; functional while server running.
* Deleting own messages - Delete option displayed for all, incl. others' messsages, but will alert and prevent others' message deletion.
* Deleting will compare display name used to sign in with sender name. No check for further logins under same name, no unique user ID.
* Design and interface very basic, I focused on functionality.
* I used chrome to test it, if running/(re)starting, may require Crtl+Shift+R (Windows) and clearing localStorage.
* Channel creation requires reloading of page to be viewed by all clients (no websocket here).
