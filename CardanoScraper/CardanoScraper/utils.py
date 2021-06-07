import os
import shutil


csv_path = 'Data/csv/'
raw_data_path = 'Data/raw/'


def save_to_html(page, content):
	html_file = f'cardano-{page}.html'
	html_path = raw_data_path + html_file
	with open(html_path, 'wb') as file:
		file.write(content)
		print(f'Saved file to: {html_path}')


def create_data_directory():
	# create Date directory
	os.makedirs('Data/csv', exist_ok=True)
	os.makedirs('Data/raw', exist_ok=True)


create_data_directory()
