# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.admin import Admin  # noqa: E501
from swagger_server.models.id import Id  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAdminsController(BaseTestCase):
    """AdminsController integration test stubs"""

    def test_dump_db(self):
        """Test case for dump_db

        dump the database as a json object
        """
        response = self.client.open(
            '/api/admin',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_load_db(self):
        """Test case for load_db

        load set of IDs records from json object
        """
        IdentityItems = [Id()]
        response = self.client.open(
            '/api/admin',
            method='POST',
            data=json.dumps(IdentityItems),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
