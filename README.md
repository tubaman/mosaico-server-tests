# mosaico-server-tests

These are tests for the Mosaico backend API endpoints.  Developers can
use these to verify their own server implementations.

These tests pass against [mosaico
v0.15](https://github.com/voidlabs/mosaico/releases/tag/v0.15)
and [django-mosaico
g11825a0](https://github.com/tubaman/django-mosaico/commit/11825a0).

## Setup

Inside a virtualenv, run: `pip install -r requirements`

## Running

Inside the virtualenv set the following environment variables:

   * `MOSAICO_URL` (default: http://127.0.0.1:9006) - This is the url of your mosaico server.

then run: `nosetests`
