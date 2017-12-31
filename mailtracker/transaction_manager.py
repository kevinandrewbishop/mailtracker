from time import sleep
import csv, json
import os

class TransactionManager():
	'''
	Tracks the transactions in the database and monitors the email folder
	for new transactions. Has "run" method that checks for new transactions
	every so many seconds.
	'''
	def __init__(self, email_client, outfile, regex):
		self.client = email_client
		self.url = outfile
		self.set_regex(regex)

	def read_db(self):
		'''
		Reads the transactions in the database.
		Currently the only "database" accepted is a json file.
		'''
		if not os.path.exists(self.url):
			return None
		if self.url.endswith('json'):
			data = json.load(open(self.url))
		return data

	def get_max_id(self):
		'''
		Get ID of most recently aquired email.
		'''
		data = self.read_db()
		if data is None:
			return 0
		max_ =  data[-1]['id']
		return int(max_)

	def set_regex(self, regex = None):
		'''
		Set the regular expression to be passed to the EmailClient.
		'''
		self.regex = regex

	def check_transactions(self):
		'''
		Checks whether there are new transactions.
		If so, adds transaction to database.
		'''
		self.client.reconnect()
		message_id = self.get_max_id()
		while message_id < self.client.num_messages:
			message_id += 1
			record = self.client.read_message(str(message_id), self.regex)
			print('Record found: %s' %record)
			self.update_transactions(message_id, record)

	def update_transactions(self, message_id, record):
		'''
		Adds new transactions to database.
		'''
		data = self.read_db()
		if data is None:
			data = list()
		record['id'] = message_id
		data.append(record)
		json.dump(data, open(self.url, 'w'))

	def run(self, seconds = 30):
		'''
		Runs loop to check and update transactions every seconds.
		'''
		while True:
			print('Checking Transactions...')
			self.check_transactions()
			sleep(seconds)
