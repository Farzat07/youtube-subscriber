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

## Whiteboard

The following is the initial version of the whiteboard:

![Whiteboard 1](images/Whiteboard1.png)

The data collector fetches the RSS feed of YouTube Channels/Playlists for new videos.
The original design had it storing the list of subscriptions to fetch in memory,
not updating it by re-querying the database but instead by getting instructions
from the data analyser. The only interactions with the database were getting the
subscriptions list at startup and saving new videos after each fetch.

The data analyser is the one that actually controls the subscription list by adding/deleting
them. It too keeps the list of subscriptions in memory, and periodically fetches
additional video details (duration) using [yt-dlp](https://github.com/yt-dlp/yt-dlp),
writing them to the database.

Finally we have the Flask app, which serves the data using an API. It also has the
functionality of modifying the subscriptions list, but not by itself as it has to
message the Data analyser through the message queue. This is because scraping YouTube
might be needed to convert channel URLs to feed links, for which the data analyser
is more suited.

However, as the development progressed, the whiteboard structure changed to the following:

![Whiteboard 2](images/Whiteboard2.png)

There are many changes, which I will list with the reason:

1. PostgreSQL was replaced with MongoDB as I decided not to wait before learning
SQL (see the SQL vs NoSQL section for more details).
2. Message Queues are replaced by direct access to the database. As I was creating
the MVP, I just allowed each application to directly access/manipulate the database
to save time. As I did so, I realised that doing so made more sense than keeping
the whole list of subscriptions in-memory for both the data analyser and collector.
Instead, both would periodically loop through the subscriptions and update some
as appropriate.
3. The data analyser no longer uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) as
it was overkill. Instead, web scraping done directly, as it has a lower chance of
failing ([yt-dlp](https://github.com/yt-dlp/yt-dlp) fetches many details about a
video increasing the points of failure and the chance of being blocked by YouTube).
To top that off, YouTube blocks all calls to video URLs from non-residential IP
addresses without login, which meant that the YouTube API had to be used in production.
4. As [yt-dlp](https://github.com/yt-dlp/yt-dlp) was no longer used, it made no
sense to separate the fetching of the feed URLs from the API server. The channel
URLs were not blocked by YouTube, so only web scraping was used.

## SQL vs NoSQL

NoSQL has some advantages - it is easier to scale horizontally, and in our example
you only need one collection(table) for the app (no `JOIN` statements). It also eliminates
the need to create a schema.

It also has a couple of disadvantages. Whenever I want to deal with a subscription
object, I have to hold all the corresponding videos in memory, which can scale badly
(many channels have millions of videos over the years). I also lose the ability to
perform operations on videos only. For example, if I want to count the number of
videos a subscription holds, I have to count in the python code, and if I want to
update one video, I have to update the whole videos list.

Furthermore, when I add the users collection (there was initially a plan to add users)
the advantage of needing only one collection will be lost.

Why did I choose NoSQL then? The deciding factor was familiarity. I had already used
MongoDB before and felt comfortable with its JSON-like syntax. I was set on learning
SQL, but that was going to take some time and I did not want to wait until I learned
it to start the project. Now that I am taking the [Databases](https://www.colorado.edu/program/data-science/databases)
specialisation though, if I were to redo the project I would definitely use SQL.

## Requirements

### User requirements

1. The user should be able to add subscriptions using their YouTube URLs (channels
or playlists).
2. The user should be able to set and modify the duration between fetches for each
subscription (some may upload more frequently than others).
3. The user should be able to delete subscriptions.
4. The user should be able to see the videos of each subscription along with the
duration of each video.
5. New videos (added since last time viewed) should be indicated to the user.

### System requirements

1. The application should be able to verify valid YouTube URLs.
2. The application should be able to identify valid subscription.
3. The application should be able to convert channel/playlist URLs to feed links.
4. The flask application should have CRUD APIs set up.
5. The data collector should be able to fetch each subscription with the appropriate
interval between fetches (set duration + <= 60s).
6. The data collector should be able to identify new/updated videos.
7. The data analyser should update all non-analysed videos in each iteration.
8. The data analyser should get the correct duration (as long as the video is not
private for example).
9. The database (MongoDB in this example) should store the data persistently.
10. The React.js application should be able to correctly communicate with the appropriate
APIs from the flask application.

All of these are easy to test. That being said, some of them, like 5., would take
a considerable time to test, even for an integration test. For the purpose of this
project, only tests taking under a minute were allowed into the integration test.

## A breakdown of the project directory

Let's start with the `components/` directory:

- `videos.py` defines the video datatype and a function which generates an object
from a feed item.
- `database.py` prepares the appropriate database collection for the `Subscription`
class.
- `subscriptions/` contains `typing.py`, which defines how the dictionary form of
the subscriptions (for [mypy](https://www.mypy-lang.org/) typing of the database
collection), while `main.py` contains the actual `Subscription` class, which has
the appropriate functions for fetching the RSS feed and database CRUD operations.
- `extractor/` contains functions designed to extract information about a YouTube
object. It is sometimes done from the URL directly (such as obtaining a Playlist's
feed link), or by web scraping (such as that of a Channel), or even by YouTube's
API (such as the duration of a video). Most of these functions accept html input
to facilitate mocking during tests.

Note that you do not need to setup YouTube API at all for any of the functions
unless you are running it on a non-residential server. YouTube API will only be
used if a key is provided as an environment variable.

### Data collector

It is stored in the `data_collector/` directory.

`utils.py` defines the core function that actually loops through the collection,
identifies which subscriptions are due to be fetched, and calls the `.fetch()` function
on them. `__main__()` imports that function and runs it periodically (every minute).

This design was chosen to make integration testing easier. Instead of having to call
a separate process, one can just import the `collect_data()` function and call it
to test the outcome. In production, the process is run by calling `python -m data_collector`,
which automatically runs the `__main__.py` file.

Most of the heavy-lifting is done by the `.fetch()` function from the `Subscription`
component, which is thoroughly tested in the `feed.py` unit test.

### Data Analyser

It is stored in the `data_analyser/` directory.

This is divided into `utils.py` and `__main__.py` for the same reason as the data
collector. The main difference is that the main function in `utils.py` is factored
into smaller functions. This makes it easy to write very specific unit tests.

### Flask application

It is stored in the `api/` directory.

While some helper functions are stored in `utils.py`, most of the functions are stored
in `__init__.py`, including flask's `app` object. This allows it to be easily found
by wsgi applications (`api:app`) as `import api` will import `__init__.py` automatically.

I did not use the same structure as the data collector or analyser as the flask
endpoints are not easily testable using unit tests as the other two. Instead, the
main testing will be done in integration tests using `from api import app`.

The flask app mostly implements a REST API interface for the front-end.

### React.js app

It is stored in the `front-end/` directory.

It is a basic web application with form functionality for CRUD operations. The main
code can be found in the `src/` subdirectory. It communicates with the flask application
using REST API.

When a subscription is selected, its videos are displayed and `last_viewed` is set
to that point in time. New videos since the last view will have a special indicator
over them.

### Tests

All tests are in the `tests/` directory. They are divided into two types:

#### Unit tests

These are the python scripts right under the `tests/` directory. Each file tests
a different function or area of the code. Unit tests are designed to test a specific
functionality, and are expected to be FIRST: Fast, Isolated, Repeatable, Self-validating,
and Timely. This means that **MOCKS** are heavily used, as external dependencies
would otherwise slow down the execution of the code and the tests would not be isolated,
as failure of the test could be caused by a problem with the external dependency
instead of the code itself. **FAKE DATA**, which is stored in the `data/` subdirectory,
is necessary too to empower the mocks to be real-like.

A few utilities to implement the mocks are stored in the `utils/` subdirectory. Specialised
packages were also installed, such as `mongomock`, which creates very realistic and
fast mocks of MongoDB databases.

#### Integration tests

These are stored in the `integration/` subdirectory, and they test how well different
parts of the application work with each other. This means that mocks/fake data would
not be used normally, as these often mask the functionality of the other components
with which we want to test the integration. This means that the real database instance
has to be used (in an isolated testing area). YouTube API calls are also used when
testing on the production server, while local testing uses web scraping of real
URL calls.

In addition, instead of calling internal function, the main functions of each of
the data collector and analyser are called to simulate the real function. Flask also
provides a way to simulate real API calls using `app.test_client()`.
