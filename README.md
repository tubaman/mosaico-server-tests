# mosaico-server-tests

These are tests for the Mosaico backend API endpoints.  Developers can
use these to verify their own server implementations.

## Setup

Inside a virtualenv, run: `pip install -r requirements`

## Running

Inside the virtualenv set the following environment variables:

   * `MOSAICO_URL` (default: http://127.0.0.1:9006) - This is the url of your mosaico server.

then run: `nosetests`
