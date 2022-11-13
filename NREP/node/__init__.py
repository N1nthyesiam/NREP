import socket, threading, requests, rsa, time
from urllib.parse import urljoin
from NREP.utils.logpong import Debug as debug
from NREP.node.pipe import Pipe

class Node:
	tbuf = 1024
	def __init__(self, config):
		debug.log("Initializing Node...")
		self.config = config
		self.configurate(self.config)
		self.setup()
		debug.log('Node started successful!')
		debug.log(f'Running on {self.host} port {self.port}')

	def print_pipes_count(self):
		debug.log(f"Pipes: {len(self.pipes)}/{self.max_connections}{' '*(self.max_connections//10)}", end='\r')

	def configurate(self, config):
		self.location = config.location
		self.income_socket = socket.socket()
		self.host = socket.gethostbyname(config.host)
		self.port = config.port
		self.beacon_url = config.beacon_url if "beacon_url" in config.config else ""
		self.max_connections = config.max_connections
		self.clean_interval = config.clean_interval
		self.main_thread = threading.Thread(target=self.main)
		self.cleaner_thread = threading.Thread(target=self.cleaner)
		if("privatekey" not in config.config or "publickey" not in config.config):
			pubk, privk = rsa.pkcs1.key.newkeys(2048)
			privk = privk.save_pkcs1().decode()
			pubk = pubk.save_pkcs1().decode()
			config.update({"privatekey": privk, "publickey": pubk})
		self.pub_key = config.publickey
		self.priv_key = config.privatekey

	def setup(self):
		self.income_socket.bind((self.host, self.port))
		self.pipes = []
		self.income_socket.listen(self.max_connections)
		self.main_thread.start()
		self.cleaner_thread.start()
		if(self.beacon_url):
			data = {
				"location": self.location,
				"host": self.host,
				"port": str(self.port),
				"pubk": self.pub_key
			}
			try:
				node_binding = requests.post(urljoin(self.beacon_url, "enroll"), json = data)
				debug.log("Successful listed on target beacon" if node_binding else f"Can't' list on target beacon")
			except:
				debug.log("Can't connect to the beacon")

	def cleaner(self):
		while True:
			for i in self.pipes:
				if(not i.alive):
					self.pipes.remove(i)
			self.print_pipes_count()
			time.sleep(self.clean_interval)

	def main(self):
		try:
			while True:
				if(len(self.pipes) <= self.max_connections):
					conn, addr = self.income_socket.accept()
					client = Pipe(conn, self.priv_key)
					self.pipes.append(client)
					self.print_pipes_count()
		finally:
			debug.err("Node closed by critical error!")
			self.income_socket.close()

	


