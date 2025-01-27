# locust-coding-challenge

## Before deploying in production

### Password storing

We store the hashed password using PBKDF2 with SHA-256 and a work factor of 260,000.
Maybe we would consider something more secure.

We would also improve the access_token management (by setting expirations and being able to refresh a token, for example).

### Environment variables

Currently we just use the defaults that are in [`config.py`](server/config.py).
For production we would create secrets (eg. in AWS or GCP).

### Input validation for routes and overall error handling

We would validate the endpoints' inputs as well as add more error handling over the whole project.

### Database

The way the database is initialised is not ideal.
The `/initdb` endpoint does not require authentication which means anybody could simply wipe the database.
Instead of an endpoint, we would want to use a tool, eg. Flask-Migrate, that can handle everything database-related (initialisation, migrations, rollbacks, etc…).

### How we measure time

We currently measure time with `datetime.now()`.
Instead we would want to use a monotonic method.

Also, we make the program sleep for `interval` seconds but that does not take into account the time it takes to run the while-loop.
If we want to be precise we would take that into account.

### Tests

I have skipped tests entirely but we would want both unit tests and integration tests, where possible.
