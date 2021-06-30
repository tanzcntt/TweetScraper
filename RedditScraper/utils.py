import os

csv_path = 'Data/csv/'
json_path = 'Data/json/'


class Utils:
	def __init__(self):
		pass

	def colors_mark(self):
		colors = {
			'header': '\033[95m',
			'okblue': '\033[94m',
			'okcyan': '\033[96m',
			'okgreen': '\033[92m',
			'warning': '\033[93m',
			'fail': '\033[91m',
			'endc': '\033[0m',
			'bold': '\033[1m',
			'underline': '\033[4m',
		}
		return colors

	def create_data_directory(self):
		if os.path.isdir(csv_path) is False:
			os.makedirs(csv_path, exist_ok=True)
			os.makedirs(json_path, exist_ok=True)
		else:
			pass
	# color = colors_mark()

	def show_message(self, message, colour, data):
		print(f"{message}: {self.colors_mark()[colour]}{data}{self.colors_mark()['endc']}")


Utils().create_data_directory()
