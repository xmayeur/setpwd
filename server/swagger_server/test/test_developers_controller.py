# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.id import Id  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDevelopersController(BaseTestCase):
    """DevelopersController integration test stubs"""

    def test_get_identity(self):
        """Test case for get_identity

        get an existing identity
        """
        query_string = [('uid', 'uid_example')]
        response = self.client.open(
            '/api/ID',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_identity(self):
        """Test case for post_identity

        Add a new identiy
        """
        IdentityItem = Id()
        response = self.client.open(
            '/api/ID',
            method='POST',
            data=json.dumps(IdentityItem),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_identity(self):
        """Test case for put_identity

        Update new identiy
        """
        IdentityItem = Id()
        response = self.client.open(
            '/api/ID',
            method='PUT',
            data=json.dumps(IdentityItem),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
