


def server_has_valid_ami(server):
    return server and server.get('Ami') and server.get('Ami').get('Name')
