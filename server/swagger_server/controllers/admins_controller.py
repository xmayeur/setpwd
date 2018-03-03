import connexion
import six

from swagger_server.models.id import Id  # noqa: E501
from swagger_server import util
from swagger_server import crypto_helpers as c


def delete_identity(IdentityItem=None):  # noqa: E501
    """Delete an existing identiy

    Delete ID tag &amp; identity # noqa: E501

    :param IdentityItem: Identity item to add
    :type IdentityItem: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        IdentityItem = Id.from_dict(connexion.request.get_json())  # noqa: E501
        aes = c.AEScipher()
        
        if aes.remove(IdentityItem.id, IdentityItem.password):
            msg = {'status': 201, 'message': 'Identity %s removed' % IdentityItem.id}
        else:
            msg = {'status': 400, 'message': 'Error removing Identity %s' % IdentityItem.id}
        aes.close()
        
    return msg
