import threading
import time
from NREP.core.NREPClient import SimpleClient, SimpleBeaconManager, SimplePathTracer

class Client():
	def __init__(self):
		beacon = SimpleBeaconManager("http://localhost")
		nodes = beacon.get_nodes()
		SimplePathTracer.trace_path(nodes)
		points, keys = SimpleBeaconManager.get_wpk(nodes)
		manager = SimpleClient(points, keys)
		self.sock = manager.connect('2ip.ru:80')
		print('connected')
		self.sock.send(b"GET / HTTP/1.1\r\nHost:2ip.ru\r\n\r\n")
		self.main()

	def main(self):
		while True:
			print(self.sock.recv(1024))

for _ in range(1):
	threading.Thread(target=Client).start()
	time.sleep(0.3)
