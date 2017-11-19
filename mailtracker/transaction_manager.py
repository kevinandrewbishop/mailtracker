from time import sleep
import csv
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
		Currently the only "database" accepted is a CSV.
		'''
		if not os.path.exists(self.url):
			return None
		with open(self.url) as f:
			data = [item for item in csv.reader(f)]
		return data

	def get_max_id(self):
		'''
		Get ID of most recently aquired email.
		'''
		data = self.read_db()
		if data is None:
			return 0
		max_ =  data[-1][0]
		if max_ == 'id':
			return 0
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
			record = self.client.read_message(str(message_id), self.regex)[0]
			record = list(record)
			print('Record found: %s' %' '.join(record))
			self.update_transactions(message_id, record)

	def update_transactions(self, message_id, record):
		'''
		Adds new transactions to database.
		'''
		with open(self.url, 'a') as f:
			writer = csv.writer(f)
			writer.writerow([message_id] + record)

	def run(self, seconds = 30):
		'''
		Runs loop to check and update transactions every seconds.
		'''
		while True:
			print('Checking Transactions...')
			self.check_transactions()
			sleep(seconds)
