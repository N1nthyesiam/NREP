from NREP.core.package import Handshake
import socket, requests
from urllib.parse import urljoin

class SimpleClient():
    def __init__(self, waypoints, keys):
        self.waypoints = waypoints[1:]
        self.entry_point = waypoints[0]
        self.keys = keys

    def connect(self, target, version = "0.1", encryption = False):
        
        handshake = Handshake.put(self.waypoints + [target],
                                version,
                                encryption,
                                self.keys)
        address = self.entry_point.split(':')
        sock = socket.socket()
        sock.connect((address[0], int(address[1])))
        sock.sendall(handshake)
        sock.recv(1)
        return sock

class SimpleBeaconManager():
    def __init__(self, beacon_url):
        self.url = beacon_url
    
    def get_nodes(self):
        nodes = requests.get(urljoin(self.url,'/nodes')).json()
        return nodes

    def get_nodes_from(self, country, region):
        try:
            listing = self.get_nodes()
            nodes = listing[country][region]
            return nodes
        except KeyError:
            raise KeyError("Region not found")

    def get_wpk(self, nodes):
        points = [nodes[i]['host']+":"+nodes[i]['port'] for i in nodes]
        keys = [nodes[i]['publickey'] for i in nodes]
        return points, keys