#!/usr/bin/env python3

import connexion
from swagger_server import encoder

application = None

def main():
    global application
    application = connexion.App(__name__, specification_dir='./swagger_server/swagger/')
    application.app.json_encoder = encoder.JSONEncoder
    application.add_api('swagger.yaml', arguments={'title': 'local password vault API'})
    application.run(port=8080)


if __name__ == '__main__':
    main()
