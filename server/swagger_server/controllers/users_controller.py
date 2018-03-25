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


def get_identity(uid):  # noqa: E501
    """get an existing identity

    By passing a user ID tag, get the associated identity (username, password) # noqa: E501

    :param uid: user ID tag
    :type uid: str

    :rtype: Id
    """
    aes = c.AEScipher()
    user, pwd = aes.read(uid=uid)
    aes.close()
    if user != '':
        return {'status': 200, 'username': user, 'password': pwd}
    else:
        return {'status': 400, 'error': 'uid not found %s' % uid}


def post_identity(IdentityItem=None):  # noqa: E501
    """Add a new identiy

    Adds an new ID tag &amp; identity # noqa: E501

    :param IdentityItem: Identity item to add
    :type IdentityItem: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        IdentityItem = Id.from_dict(connexion.request.get_json())  # noqa: E501
        aes = c.AEScipher()
        user, _ = aes.read(IdentityItem.id)
        if user != '':
            aes.close()
            return {'status': 409, 'error': 'Cannot post an existing identity!'}
        else:
            aes.save(IdentityItem.id, IdentityItem.username, IdentityItem.password)
            aes.close()
            return {'status': 200, 'message': 'New identity successfully created'}


def put_identity(IdentityItem=None):  # noqa: E501
    """Update new identiy

    Update and existing ID tag &amp; identity # noqa: E501

    :param IdentityItem: Identity item to add
    :type IdentityItem: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        IdentityItem = Id.from_dict(connexion.request.get_json())  # noqa: E501
        aes = c.AEScipher()
        user, _ = aes.read(IdentityItem.id)
        if user != '':
            aes.save(IdentityItem.id, IdentityItem.username, IdentityItem.password)
            aes.close()
            return {'status': 200, 'message': 'New identity successfully updated'}
        else:
            aes.close()
            return {'status': 400, 'error': 'Identity %s not found' % IdentityItem.id}
