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

## Before deploying in production

### Environment variables

Currently we just use the defaults that are in [`config.py`](config.py).
For production we would create secrets (eg. in AWS or GCP).

### Input validation for routes and overall error handling

We would validate the endpoints' inputs as well as add more handling over the whole project.

### Database

The way the database is initialised is not ideal.
Instead of an endpoint, we would want to have scripts to initialise and migrate the database (eg. using Flask-Migrate).

### Tests

I have skipped tests entirely but one would want to have both unit tests and integration tests, where possible.
