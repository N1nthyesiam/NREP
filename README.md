# About NREP
This is an exemplary, non-reference implementation of NREP/RecRoll.

NREP, NetREP is a decentralized data transmission network project designed for anonymous and secure interaction with the Internet and blocking bypass.
The main provisions of the NREP/RecRoll protocol are given in the [NREP_v0.1_reference](https://github.com/N1nthyesiam/NREP/blob/main/NREP_v0.1_reference.txt).
> There may be inaccuracies, some things have changed in NREP v0.1.2

# Installation
You can use pip to install this package:
```pip install NREP```

You also can use the [wheel](https://github.com/N1nthyesiam/NREP/tree/main/dist) to install the package or install it via [PyPI](https://pypi.org/project/NREP/).

> Using examples for versions younger than v0.1.2 undesirable.  
Previous releases have been corrupted and are not recommended for use.

# Bit of theory
NREP redirects your traffic through several network nodes in such a way as to erase the maximum number of indirect signs.
For each connection (socket), a _pipe_ is created that passes through several nodes.

Different sets of nodes can be used for different connections, which increases anonymity and security (even when connected to the same server). 
The traffic required to create a pipe (handshake) is also encrypted in a special way.

Creating a pipe takes some time and piping is used to speed up the connection (one connection can be used for several consecutive requests).
On average, the difference in speed between direct connection and NREP pipe is ±5%

# Usage
NREP can be used to bypass the locks set by the provider or as an alternative to tor in cases where the use of tor is impossible.

For example, we will deploy the network locally to bypass the blocking of some site (e.g. google.com )

## Configuring the Node
After [installing](#installation) the package, create a file node.py
```python
from NREP.node import Node
from NREP.utils.spec import Config

config = Config('config.json')
node = Node(config)
```
Now we create the node configuration.
```json
{
 "location": "MAIN-LOC1",
 "max_connections": 100,
 "host": "HOST",
 "port": 5689,
 "clean_interval": 0.1,
 "beacon_url": "NODE_URL",
}
```
The "location" field contains information about the location of the node in the format (region-location).  
The "max_connections" field sets the maximum number of open tunnels (pipes).  
"clean_interval" - pipe pool cleaning frequency in seconds.
"beacon_url" contains a link to the beacon (we will configure it below).  
You fill in the host and port fields at your discretion, the main thing is that your system should be able to use them for node setup.

## Configuring the beacon
Now we are setting up the beacon. It is needed to link the node and the end user.  
Therefore, it should be within reach of both the node and the client (you).

Creating a file beacon.py
```python
from NREP.beacon import Beacon
from NREP.utils.spec import Config

config = Config('beacon_config.json')
node = Beacon(config)
```
And the configuration to it.
```json
{
	"location": "not used",
	"host": "BEACON_HOST",
	"port": 80,
	"nodelist": "nodes_listing.json"
}
```
The "location" field will be used in future updates.  
Everything is the same with the port and the host.
The "nodelist" field contains the path to the node listing file.
```json
{
    "MAIN": {
        "LOC1": {
            
        }
    }
}
```
All locations must be registered in it, and nodes can also be added manually, if necessary.
Little e.g: 
```json
{
    "MAIN": {
        "LOC1": {
            "node1": {
              "host": "localhost",
              "port": "5689",
              "publickey": "PKCS1_PUBLIC_KEY"
            }
        }
    }
}
```

## Configuring http2nrep bridge
The main part is ready.  
It remains only to configure the bridge so that we can conduct http-traffic through NREP.

It is quite simple to do this, it is enough to import the bridge class and initialize it.

```python
from NREP.bridge.http2nrep import Bridge

Bridge("127.0.0.1", 8080, beacon_url="http://localhost")
```
Remember that in order for everything to work, the "beacon_url" field in the node configuration and the beacon_url argument in the bridge class instance must match.

The bridge must be running on the computer from which the requests will originate.

Now everything is ready. getting started. The node should be placed outside the firewall (where the lock does not work).  
You can also combine several noвes, if necessary, they will all сщттусе the specified beacon.

After making sure that everything is ready, we launch the beacon, then the node and at the end the bridge.  
The bridge works as an http/https proxy and you need to connect to it accordingly.

Now you can safely use the internet. no one will be able to identify the sites or servers to which you are making requests.  
The http2nrep bridge is universal for almost all protocols that can be used with an http proxy.  

Enjoy!

> All of the above materials are available ready-made in the [examples](https://github.com/N1nthyesiam/NREP/tree/main/Examples) for the project.

# Future updates
> Here are the plans for the upcoming updates.
- Packet morphing.  
Masking of RecRoll handshakes under http-requests for better blocking bypass.
- Nodes ranking system.
- Beacons subnet.  
Combining beacons in a network to exchange node lists.
