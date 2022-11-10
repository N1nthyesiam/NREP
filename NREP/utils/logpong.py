class Debug:
	def log(*data, end="\n"):
		print("[INFO]", *data, end=end)

	def warn(*data, end="\n"):
		print("[WARN]", *data, end=end)

	def err(*data, end="\n"):
		print("[ERROR]", *data, end=end)