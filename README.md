# mosaico-server-tests

These are tests for the Mosaico backend API endpoints.  Developers can
use these to verify their own server implementations.

## Setup

Inside a virtualenv, run: `pip install -r requirements`

## Running

Inside the virtualenv set the following environment variables:

   * `MOSAICO_URL` (default: http://127.0.0.1:9006) - This is the url of your
     mosaico server.
   * `MOSAICO_DIR` (default: None) - This is your mosaico directory.
     stored.  You *must* explicitly set this one.
   * `TEST_PHOTO` (default: None) - This is the path to the image used for testing.
     It should be a jpg or png.  You *must* explicitly set this one.

then run: `nosetests`
