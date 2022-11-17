from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto import Random
from NREP.core.VersionControl import nrep_version, v
import rsa

class Handshake:
	def pick(raw_data: bytes, private_key: str, aes_block_size: int=16):
		head, version, need_encryption, separator_size, separator, waypoints, keys = Handshake.parse(raw_data)
		if(not nrep_version.is_compatible_with(version)):
			raise ValueError("incompatible versions")
		key = rsa.decrypt(keys[0], rsa.PrivateKey.load_pkcs1(private_key.encode()))
		_iv = key[:aes_block_size]
		_key = key[aes_block_size:]
		cipher = AES.new(_key, AES.MODE_EAX, nonce = _iv)
		point = cipher.decrypt(waypoints[0])
		if(len(waypoints)<2):
			return point, b''
		return point, Handshake.compare(head, version, need_encryption, separator_size, separator, waypoints[1:], keys[1:])
		

	def compare(head: bytes, version: tuple, need_encryption: bool, separator_size: int, separator: bytes, waypoints: list, keys: list):
		return b''.join((head, bytes(version), (b'\x00' if need_encryption else b'\xff'), separator_size.to_bytes(1, 'big'), separator, separator.join(waypoints), separator, separator.join(keys)))

	def put(waypoints: list, need_encryption: bool, public_keys: list, separator: bytes=b"NEXTL", aes_block_size: int=16):
		version = bytes(nrep_version)
		need_encryption = b'\x00' if need_encryption else b'\xff'
		separator_size = len(separator).to_bytes(1,'big')
		random = Random.new()
		waypoints = list(map(str.encode, waypoints))
		public_keys = list(map(str.encode, public_keys))
		for i in range(len(waypoints)):
			_key = get_random_bytes(aes_block_size)
			_iv = random.read(aes_block_size)
			waypoints[i] = AES.new(_key, AES.MODE_EAX, _iv).encrypt(waypoints[i])
			public_keys[i] = rsa.encrypt(_iv+_key, rsa.PublicKey.load_pkcs1(public_keys[i]))
		return b''.join((b'\xf2', version, need_encryption, separator_size, separator, separator.join(waypoints), separator, separator.join(public_keys)))

	def parse(raw_data: bytes):
		try:
			head = raw_data[:1]
			if(head!=b'\xf2'):
				raise ValueError("wrong head")
			version = v.from_bytes(raw_data[1:4])
			separator_size = int.from_bytes(raw_data[5:6], 'big')
			separator = raw_data[6:6+separator_size]
			data = raw_data[6+separator_size:].split(separator)
			dl = len(data)
			if(dl%2!=0):
				raise ValueError("broken payload")
			return 	head,\
					version,\
					raw_data[4:5]!=b'\xff',\
					separator_size,\
					separator,\
					data[:dl//2],\
					data[dl//2:]
		except:
			raise ValueError('incorrect handshake')

def get_nodes_from_listing(nodelisting: dict):
	return {node:dict(nodelisting[region][location][node], region=region, location=location) for region in nodelisting for location in nodelisting[region] for node in nodelisting[region][location]}