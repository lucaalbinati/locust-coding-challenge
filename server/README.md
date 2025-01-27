# locust-coding-challenge server

A Flask-based API for managing CPU usage in test runs.

## Installation

### Run using Docker

Build the Docker image with:

```
make build
```

Run the application with:

```
make up
```

### Setup the database

The database will need to be initialised the first time the server runs.
Do this by making a `GET` request to `/initdb`.

This will create a user with username `demo` and password `demo123`.
