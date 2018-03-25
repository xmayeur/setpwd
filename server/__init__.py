#!/usr/bin/env python3

import connexion
from swagger_server import encoder
from swagger_server.controllers.admins import adm


app = connexion.App(__name__, specification_dir='./swagger_server/swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'local password vault API'})
application = app.app
app.app.register_blueprint(adm, url_prefix='/admins')
app.run(port=8080)

