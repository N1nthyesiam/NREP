import socket
from flask import Flask, render_template, request, redirect, Response
from NREP.utils.logpong import Debug as debug

class Beacon:
	def __init__(self, config):
		debug.log("Initializing Beacon...")
		self.config = config
		self.configurate(self.config)
		self.setup()
		debug.log('Beacon started successful!')
		debug.log(f'Running on {self.host} port {self.port}')

	def configurate(self, config):
		self.location = config.location
		self.app = Flask(__name__)
		self.host = socket.gethostbyname(config.host)
		self.port = config.port
		self.nodelist = config.nodelist

	def setup(self):
		self.app.add_url_rule("/nodes", view_func=self.get_nodes)
		self.app.run(host=self.host, port=self.port)

	def get_nodes(self):
		with open(self.nodelist, "r") as nodes:
			return nodes.read()
