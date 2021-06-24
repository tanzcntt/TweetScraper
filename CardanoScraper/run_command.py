import getopt
import os, sys
import time
import threading
from datetime import datetime, timedelta

# ================================================
# Give param to command
# ================================================
argumentList = sys.argv[1:]

options = 'm:'

long_options = ['mode']
mode = 'latest'
sources = ['Carda', 'Iohk', 'Coindesk']
try:
	# Parsing argument
	arguments, values = getopt.getopt(argumentList, options)
	for currentArgument, currentValue in arguments:
		if currentArgument in ('-m', '--mode'):
			mode = str(currentValue)
except getopt.error as err:
	print(err)

print(mode)


class MyThread(threading.Thread):
	def __init__(self, source, mode):
		super().__init__()
		self.source = source
		self.mode = mode

	def run(self):
		start_time = time.time()
		try:
			# thread_lock.acquire()  # force threads to run synchronously
			run_command(self.source, self.mode)
			# thread_lock.release()  # release the lock whe no longer required
		except NameError:
			print(NameError)
		end_time = time.time()
		print(f"\n\n\ntotal time: {timedelta(seconds=(end_time - start_time))}")


def run_command(source, mode):
	for source_ in sources:
		if source == source_:
			check_condition(source=source_, mode=mode)


def check_condition(source, mode):
	if mode == 'latest':
		command = f'scrapy crawl {mode}{source}'
		os.system(command)
	elif mode == 'all':
		command = f'scrapy crawl {mode}{source}'
		os.system(command)
	else:
		print('Invalid Mode')


# ================================================
# Synchronizing threads
# ================================================
# A new lock is created
thread_lock = threading.Lock()  # allow to synchronize threads
threads = []

for i, value in enumerate(sources):
	thread = MyThread(f'{value}', mode)
	thread.start()
	threads.append(thread)


# wait for all threads to complete
for t in threads:
	t.join()
print("Crawling completed!")
