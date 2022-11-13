import socket, requests, random
from NREP.core.package import Handshake
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
        self.last_update = 0
        self.nodes = {}
    
    def get_nodes(self):
        upd = self.check_beacon_updates()
        if(upd>self.last_update):
            self.nodes = requests.get(urljoin(self.url,'/nodes')).json()
            self.last_update = upd
        return self.nodes

    def check_beacon_updates(self):
        return float(requests.get(urljoin(self.url,'/lastupdate')).text)

    def get_nodes_from(self, region, location):
        try:
            listing = self.get_nodes()
            nodes = listing[region][location]
            return nodes
        except KeyError:
            raise KeyError("Region not found")

    def get_wpk(nodes):
        points = [nodes[i]['host']+":"+nodes[i]['port'] for i in nodes]
        keys = [nodes[i]['publickey'] for i in nodes]
        return points, keys

class SimplePathTracer():
    def trace_path(nodes, rex="*", min_path_length=3, max_path_length=3, strict_path_length=False):
        nodes = {node:nodes[region][location][node] for region in nodes for location in nodes[region] for node in nodes[region][location]}
        if(strict_path_length and len(nodes)<max(min_path_length, max_path_length)):
            raise ValueError("Number of nodes less than required path length")
        selection = list(nodes)
        random.shuffle(selection)
        return {node:nodes[node] for node in selection[:random.randint(min(len(nodes), min_path_length), min(len(nodes), max_path_length))]}


# rex e.g [regions](locations)
# * all    ! xeclude    # select
# 
# 
# 