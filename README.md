# lastweek

## What

A simple web app for tracking what you did each week. You can file the week's
accomplishments in Markdown format and tag them, then see all your past weeks
in the History view. Clicking a tag in History view will filter to show only
weeks tagged with the given tag filter.

## Why

To review basic web development and Python. I followed [Miguel
Grinberg](https://blog.miguelgrinberg.com/)'s excellent book [Flask Web
Development](https://learning.oreilly.com/library/view/flask-web-development/9781491991725/), 2nd edition.

## Usage

First, create and activate the virtual environment and install dependencies:

    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt

To run the unit tests:

    flask test

To fill an sqlite database with test users:

    flask fill-db

This will create a bunch of users with test posts and tags. To get the
email address of a test user:

    sqlite3 data.sqlite
    SELECT email FROM users LIMIT 1;

The default password for the test users is "p@ssw0rd" (without the quotes).
You can log into the app using those credentials to see test data, or create
a new user.

To run the app locally in development mode with the sqlite database:

    flask run

And then open http://127.0.0.1:5000 in your browser. (Note that the new user
confirmation flow with email tokens is disabled in development mode.)

## License

MIT License
Copyright (c) 2021 Daniel Connelly
