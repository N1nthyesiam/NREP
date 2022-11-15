import socket, requests, random
from NREP.core.package import Handshake, get_nodes_from_listing
from urllib.parse import urljoin

class SimpleClient():
    def __init__(self, waypoints: list, keys: list):
        self.waypoints = waypoints[1:]
        self.entry_point = waypoints[0]
        self.keys = keys

    def connect(self, target: str, version: str="0.1", encryption: bool=False):
        
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

    def get_nodes_from(self, region: str, location: str):
        try:
            listing = self.get_nodes()
            nodes = listing[region][location]
            return nodes
        except KeyError:
            raise KeyError("Region not found")

    def get_wpk(nodes: list):
        points = [nodes[i]['host']+":"+nodes[i]['port'] for i in nodes]
        keys = [nodes[i]['publickey'] for i in nodes]
        return points, keys

class SimplePathTracer():
    def trace_path(nodes: list, rex: str="*", min_path_length: int=3, max_path_length: int=3, strict_path_length: bool=False):
        nodes = get_nodes_from_listing(nodes)
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