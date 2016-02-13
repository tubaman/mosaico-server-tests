import os
import unittest
from glob import glob
from urlparse import urlsplit

import requests


class MosaicoServerTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MosaicoServerTestCase, self).__init__(*args, **kwargs)
        self.base_url = os.environ.get("MOSAICO_URL", "http://127.0.0.1:9006")
        mosaico_dir = os.environ.get("MOSAICO_DIR", None)
        self.upload_dir = os.path.join(mosaico_dir, 'uploads')
        self.photo = os.environ.get("TEST_PHOTO", None)

    def clear_uploads(self):
        to_remove = glob(os.path.join(self.upload_dir, '*.png'))
        to_remove += glob(os.path.join(self.upload_dir, '*.jpg'))
        to_remove += glob(os.path.join(self.upload_dir, 'thumbnail', '*'))
        [os.remove(f) for f in to_remove]


class TestImage(MosaicoServerTestCase):

    def setUp(self):
        self.url = '/'.join([self.base_url, 'img/'])

    def do_upload(self):
        self.clear_uploads()
        files = {'file': open(self.photo, 'rb')}
        upload_url = '/'.join([self.base_url, 'upload/'])
        response = requests.post(upload_url, files=files)
        self.assertEquals(response.status_code, 200)
        uploads = response.json()['files']
        return uploads

    def test_placeholder(self):
        params = {
            'method': 'placeholder',
            'params': '166, 130',
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))

    def test_cover(self):
        uploads = self.do_upload()
        params = {
            'method': 'cover',
            'src': uploads[0]['url'],
            'params': '166,null',
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))

    def test_resize(self):
        uploads = self.do_upload()
        params = {
            'method': 'resize',
            'src': uploads[0]['url'],
            'params': '166,null',
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))


class TestUpload(MosaicoServerTestCase):

    def setUp(self):
        self.url = '/'.join([self.base_url, 'upload/'])
        self.clear_uploads()

    def assertValidURL(self, url):
        parts = urlsplit(url)
        if not any([parts.netloc, parts.path]):
            raise AssertionError("%s is not a URL" % url)

    def test_upload(self):
        photo_file = open(self.photo, 'rb')
        files = {'file': photo_file}
        response = requests.post(self.url, files=files)
        photo_filename = os.path.basename(photo_file.name)
        self.assertEquals(response.status_code, 200)
        data = response.json()
        file_data = data['files'][0]
        self.assertEquals(file_data['deleteType'], 'DELETE')
        self.assertValidURL(file_data['deleteUrl'])
        self.assertNotEquals(file_data['name'], '')
        self.assertEquals(file_data['originalName'], photo_filename)
        self.assertEquals(file_data['size'], os.path.getsize(self.photo))
        self.assertValidURL(file_data['thumbnailUrl'])
        self.assertEquals(file_data['type'], None)
        self.assertValidURL(file_data['url'])


class TestDownload(MosaicoServerTestCase):

    def setUp(self):
        self.url = '/'.join([self.base_url, 'dl/'])

    def test_email(self):
        data = {
            'action': 'email',
            'rcpt': 'example@example.org',
            'subject': 'test subject',
            'html': "<html></html>",
        }
        response = requests.post(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertRegexpMatches(response.text, r"^OK: 250 OK id=.*$")

    def test_download(self):
        data = {
            'action': 'download',
            'filename': 'email.html',
            'html': "<html></html>",
        }
        response = requests.post(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers['Content-disposition'], "attachment; filename=email.html")
        self.assertEquals(response.headers['Content-type'], 'text/html')
        self.assertEquals(response.text, data['html'])
