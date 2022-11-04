from NREP.node import Node
from NREP.utils.spec import Config
from NREP.bridge.http2nrep import Bridge

config = Config('config.json')
node = Node(config)
# Bridge("127.0.0.1", 8080)