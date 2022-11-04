import socket, threading
from NREP.core.package import Handshake
import NREP.node as nn

class Pipe:
	def __init__(self, _from, key):
		try:
			self.buffer_size = nn.Node.tbuf
			self._from = _from
			self.alive = True
			target, pkg = self.get_handshake(key)
			self.setup(target, pkg)
		except:
			self.close()

	def get_handshake(self, key):
		data = self._from.recv(4096)
		self._from.send(b"\xAB")
		return Handshake.pick(data, key)

	def close(self):
		try:
			self.alive = False
			self._from.close()
			self._to.close()
		except:
			pass

	def setup(self, target, pkg):
		self._to = socket.socket()
		addr = target.rsplit(b':',1)
		self._to.connect((addr[0], int(addr[1])))
		if(pkg):
			self._to.sendall(pkg)
			self._to.recv(1)
		threading.Thread(target=self.rx).start()
		threading.Thread(target=self.tx).start()

	def tx(self):
		try:
			while True:
				recv = self._from.recv(self.buffer_size)
				if(recv):
					# print(recv)
					self._to.sendall(recv)
				else:
					self.close()
					break
		except:
			self.close()

	def rx(self):
		try:
			while True:
				recv = self._to.recv(self.buffer_size)
				if(recv):
					# print(recv)
					self._from.sendall(recv)
				else:
					self.close()
					break
		except:
			self.close()