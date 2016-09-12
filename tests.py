import os
import unittest
import posixpath
from glob import glob
from urlparse import urlsplit
from StringIO import StringIO

import requests
from bs4 import BeautifulSoup
from PIL import Image


class MosaicoServerTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MosaicoServerTestCase, self).__init__(*args, **kwargs)
        self.base_url = os.environ.get("MOSAICO_URL", "http://127.0.0.1:9006")
        self.photo_path = os.path.join(os.path.dirname(__file__), 'test.png')


class TestImage(MosaicoServerTestCase):

    def setUp(self):
        self.url = posixpath.join(self.base_url, 'img/')

    def do_upload(self):
        files = {'file': open(self.photo_path, 'rb')}
        upload_url = posixpath.join(self.base_url, 'upload/')
        response = requests.post(upload_url, files=files)
        self.assertEquals(response.status_code, 200)
        upload, = response.json()['files']
        return upload

    def test_placeholder(self):
        params = {
            'method': 'placeholder',
            'params': '166, 130',
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))
        image = Image.open(StringIO(response.content))
        self.assertEqual(image.size, (166, 130))

    def test_cover(self):
        upload = self.do_upload()
        photo = Image.open(open(self.photo_path, 'rb'))
        new_size = tuple([d/2 for d in photo.size])
        params = {
            'method': 'cover',
            'src': upload['url'],
            'params': ','.join([str(d) for d in new_size]),
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))
        image = Image.open(StringIO(response.content))
        self.assertEqual(image.size, new_size)

    def test_cover_one_null(self):
        """Cover shouldn't resize when a null is passed as a size param"""
        upload = self.do_upload()
        photo = Image.open(open(self.photo_path, 'rb'))
        new_width = photo.size[0] / 2
        params = {
            'method': 'cover',
            'src': upload['url'],
            'params': "%d,null" % new_width,
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))
        image = Image.open(StringIO(response.content))
        self.assertEqual(image.size, photo.size)


    def test_resize(self):
        upload = self.do_upload()
        params = {
            'method': 'resize',
            'src': upload['url'],
            'params': '166,null',
        }
        response = requests.get(self.url, params)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('image/'))
        image = Image.open(StringIO(response.content))
        self.assertEqual(image.size[0], 166)


class TestUpload(MosaicoServerTestCase):

    def setUp(self):
        self.url = posixpath.join(self.base_url, 'upload/')

    def assertValidURL(self, url):
        parts = urlsplit(url)
        if not any([parts.netloc, parts.path]):
            raise AssertionError("%s is not a URL" % url)

    def test_upload(self):
        photo_file = open(self.photo_path, 'rb')
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
        self.assertEquals(file_data['size'], os.path.getsize(self.photo_path))
        self.assertValidURL(file_data['thumbnailUrl'])
        self.assertEquals(file_data['type'], None)
        self.assertValidURL(file_data['url'])


class TestDownload(MosaicoServerTestCase):

    def setUp(self):
        self.url = posixpath.join(self.base_url, 'dl/')

    def assertValidHTML(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
        except:
            raise AssertionError("Invalid HTML: %s" % html)

    def test_email(self):
        data = {
            'action': 'email',
            'rcpt': 'example@example.org',
            'subject': 'test subject',
            'html': "<html><head></head><body><p></p></body></html>",
        }
        response = requests.post(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertRegexpMatches(response.text, r"^OK: 250 OK id=.*$")

    def test_download(self):
        data = {
            'action': 'download',
            'filename': 'email.html',
            'html': "<html><head></head><body><p></p></body></html>",
        }
        response = requests.post(self.url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers['Content-disposition'], "attachment; filename=email.html")
        self.assertEquals(response.headers['Content-type'], 'text/html')
        self.assertValidHTML(response.text)
