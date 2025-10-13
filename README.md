# YouTube Subscriber

This application runs continuously, optionally on a server, watching YouTube feeds
for new videos. This can be used to eliminate the need to subscribe to the channels
themselves or even create a Google account. It also allows you to follow YouTube
playlists.

## Technology Stack

### Back-end

- Language: Python.
- Web Framework Flask.
- [venv](https://docs.python.org/3/library/venv.html) for the virtual environment.
- Type checking using [mypy](https://www.mypy-lang.org/).
- Testing using [unittest](https://docs.python.org/3/library/unittest.html).
- Production on a Private VPS running Arch Linux.
- Production deployment using [gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/)
and [nginx](http://nginx.org/).

### Front-end

- Language: JavaScript.
- Built using [Vite](https://vite.dev/).
- Hosted on [GitHub Pages](https://pages.github.com/).
