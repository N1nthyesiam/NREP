from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto import Random
import rsa

class Handshake:
	def pick(raw_data, private_key, aes_block_size = 16):
		head, version, need_encryption, separator_size, separator, waypoints, keys = Handshake.parse(raw_data)
		key = rsa.decrypt(keys[-1], rsa.PrivateKey.load_pkcs1(private_key.encode()))
		_iv = key[:aes_block_size]
		_key = key[aes_block_size:]
		cipher = AES.new(_key, AES.MODE_EAX, nonce = _iv)
		point = cipher.decrypt(waypoints[-1])
		if(len(waypoints)<2):
			return point, b''
		return point, Handshake.compare(head, version, need_encryption, separator_size, separator, waypoints[1:], keys[1:])
		

	def compare(head, version, need_encryption, separator_size, separator, waypoints, keys):
		return b''.join((head, version[0].to_bytes(1, 'big')+version[1].to_bytes(1, 'big'), (b'\x00' if need_encryption else b'\xff'), separator_size, separator, separator.join(waypoints), separator, separator.join(keys)))

	def put(waypoints, version, need_encryption, public_keys, separator=b"NEXTL", aes_block_size = 16):
		version = tuple(map(lambda i: int(i).to_bytes(1,'big'),version.split('.')))
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
		return b''.join((b'\xf2', b''.join(version), need_encryption, separator_size, separator, separator.join(waypoints), separator, separator.join(public_keys)))

	def parse(raw_data):
		try:
			head = raw_data[:1]
			assert head==b'\xf2', f"wrong head"
			version = (raw_data[1:2], raw_data[2:3])
			separator_size = int.from_bytes(raw_data[4:5], 'big')
			separator = raw_data[5:5+separator_size]
			data = raw_data[5+separator_size:].split(separator)
			dl = len(data)
			assert dl%2==0, "broken payload"
			return 	head,\
					version,\
					raw_data[3:4]!=b'\xff',\
					separator_size,\
					separator,\
					data[:dl//2],\
					data[dl//2:]
		except:
			raise ValueError('incorrect handshake')