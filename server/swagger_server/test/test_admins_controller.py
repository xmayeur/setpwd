# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.id import Id  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAdminsController(BaseTestCase):
    """AdminsController integration test stubs"""

    def test_delete_identity(self):
        """Test case for delete_identity

        Delete an existing identiy
        """
        IdentityItem = Id()
        response = self.client.open(
            '/api/ID',
            method='DELETE',
            data=json.dumps(IdentityItem),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
