# mosaico-server-tests

These are tests for the Mosaico backend API endpoints.  Developers can
use these to verify their own server implementations.

## Setup

Inside a virtualenv, run: `pip install -r requirements`

## Running

Inside the virtualenv set the following environment variables:

   * `MOSAICO_URL` (default: http://127.0.0.1:9006) - This is the url of your
     mosaico server.
   * `MOSAICO_DIR` - This is the mosaico directory where uploads are stored.
     You *must* explicitly set this one.
   * `TEST_PHOTO` - This is the path to the image used for testing.  It should
     be a jpg or png.  You *must* explicitly set this one.

TODO: check in a standard test photo so we can remove the `TEST_PHOTO` env var.

then run: `nosetests`

Note: This test suite must be run locally on the server where mosaico
is running since it needs access to the filesystem.
