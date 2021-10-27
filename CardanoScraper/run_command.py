import os, sys
import subprocess
from tqdm import tqdm
from time import sleep
from CardanoScraper import config as cfg
from CardanoScraper.utils import *


def run_command(sources, mode):
	for source in sources:
		show_message('\n\n\n', 'okgreen', f'Start crawling: {source}!')
		check_condition(source, mode)
		show_message('', 'warning', f'Crawling {source} complete!')
		sleep(3)


def check_condition(source, mode):
	if mode == 'latest':
		command = f'scrapy crawl {source} -a mode={mode}'
		os.system(command)
	elif mode == 'all':
		command = f'scrapy crawl {source} -a mode={mode}'
		os.system(command)
	else:
		print('Invalid Mode')
		exit()


if __name__ == '__main__':
	print('main is running...')
	args = sys.argv[1:]
	mode, number_of_runs, break_time = args
	number_of_runs = int(number_of_runs)
	break_time = float(break_time) * 60 * 60

	working_directory = os.getcwd().split('/')
	working_directory.remove(working_directory[-1])
	working_directory = '/'.join(working_directory)

	time = {
		1: '1st',
		2: '2nd',
		3: '3rd',
	}
	for i in range(1, number_of_runs):
		show_message('\n\n\n', 'okcyan', f'{time[i] if i in time else f"{i}th"} Run || Break_time: {break_time/(60*60)} hour(s)')
		run_command(cfg.SOURCES, mode)
		show_message('', 'fail', f'{time[i] if i in time else f"{i}th"} Run completed!')
		show_message('', 'okcyan', 'Push data to Dhunt.')
		p = subprocess.Popen(['python3', 'submit-news.py', '-u', cfg.SITE, '-t', 'defaulttoken'], cwd=working_directory)
		p.wait()
		show_message('', 'warning', '\nCounting to next Crawl!')
		for j in tqdm(range(int(break_time))):
			sleep(1)
		# sleep(break_time)
