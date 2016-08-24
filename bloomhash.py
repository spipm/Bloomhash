'''
	Bloomhash.com, 2016
	Negative lookup table for hashes from a wordlist using a bloom filter
'''

import hashlib
import struct

from random import randint



class bloomhashLookupBuilder(object):
	""" Creates negative lookup table for password hashes using a bloom filter like structure in files """


	def __init__(self, wordlistFile, debug=False):
		self.debug = debug
		self.wordlistFile = wordlistFile
		self.hashMethods = {}	# container for hash method / output file
		
		self.bitArraySize = int(self.getLineCount(wordlistFile) * 2.0)	# this should create about 33/66 0's and 1's


	def processEntry(self, word):
		''' process a single value from the wordlist '''

		for method in self.hashMethods:
			fout = self.hashMethods[method][1]
			bloomIndex = int(self.hashMethods[method][0](word).hexdigest(),16) % self.bitArraySize

			byteIndex = bloomIndex / 8
			bitIndex = int(bloomIndex % 8)

			if self.debug:
				print "\nIndex: " + str(bloomIndex)
				print "Byte index: " + str(byteIndex)
				print "Bit index: " + str(bitIndex)

			fout.seek(byteIndex)
			character = struct.unpack('B', fout.read(1))[0]

			if self.debug:
				print "Binary before: " + bin(character)

			character |= ( 1 << bitIndex )

			if self.debug:
				print "Binary after : " + bin(character)

			fout.seek(byteIndex)
			fout.write(chr(character))


	def processFile(self):
		''' Actually process the file and build the table using the provided hash algo's '''

		with open(self.wordlistFile, 'r') as fin:
			for word in fin:
				word = word.strip('\n\r')

				self.processEntry(word)

		self.closeOutputFiles()


	def closeOutputFiles(self):
		''' Close output files '''

		for method in self.hashMethods:
			self.hashMethods[method][1].close()


	def addHashMethod(self, method):
		''' Add hash method and create output file '''

		outputFileHandler = self.prepareOutputFile(method)
		self.hashMethods[method.__name__] = [method, outputFileHandler]


	def getOutputFilename(self, method):
		''' Get filename for output '''

		return self.wordlistFile + '.bloomhash.' + method.__name__ + '.dat'


	def prepareOutputFile(self, method):
		''' Prepare config file for lookups and a file handler for the output file '''

		# Save table size and filename for lookups later
		with open(self.getOutputFilename(method) + '.size','w') as fout:
			fout.write(str(self.bitArraySize) + "\n")
			fout.write(self.getOutputFilename(method) + "\n")
			fout.write(method.__name__ + "\n")
			fout.write(self.wordlistFile + "\n")

		filename = self.getOutputFilename(method)
		fout = open(filename,'wb+')
		fout.seek((self.bitArraySize/8)+1)
		fout.write("\0")
		return fout


	def getLineCount(self, filename):
		''' Get number of newlines in a file '''

		newlineCount = 0

		with open(self.wordlistFile, 'r') as fin:
			for line in fin:
				newlineCount += 1

		return newlineCount



class bloomhashLookupper(object):
	""" Look up value in the table """

	def __init__(self, tableInfoFile):
		self.tableInfoFile = tableInfoFile

		with open(tableInfoFile,'r') as fin:
			self.tableFileSize = int(fin.readline().strip("\n"))
			self.tableFile = fin.readline().strip("\n")
			self.hashMethodName = fin.readline().strip("\n")
			self.originalFile = fin.readline().strip("\n")

		self.hashMethod = self.getMethodForHashMethodName(self.hashMethodName)
		
	
	def getMethodForHashMethodName(self, name):
		''' Get the actual method for the name of a hashing method '''

		methodTable = {
						'openssl_md5':hashlib.md5,
						'openssl_sha1':hashlib.sha1,
						'openssl_sha224':hashlib.sha224,
						'openssl_sha256':hashlib.sha256,
						'openssl_sha384':hashlib.sha384,
						'openssl_sha512':hashlib.sha512
						}

		return methodTable[name]


	def lookupValue(self, value):
		''' Accepts hexadecimal value to look up in the table '''

		bloomIndex = int(value,16) % self.tableFileSize
		byteIndex = bloomIndex / 8
		bitIndex = int(bloomIndex % 8)
		
		with open(self.tableFile, 'rb') as fin:
			fin.seek(byteIndex)
			character = struct.unpack('B', fin.read(1))[0]
			if character & ( 1 << bitIndex ) == 0:
				return False
			else:
				return True


	def lookupHashFor(self, value):
		''' Hash value and look it up in the table '''

		return self.lookupValue(self.hashMethod(value).hexdigest())



class bloomhashLookupTester(object):
	""" Class to test the lookup table for validity """

	def __init__(self, tableInfoFile, debug=False):
		self.lookupper = bloomhashLookupper(tableInfoFile)
		self.debug = debug


	def checkTable(self):
		'''
			Check the table for correctness

			Uses the original file and random samples
		'''

		if not self.originalHashTest():
			return False
		if not self.randomTest():
			return False

		return True


	def originalHashTest(self):
		'''
			Check if bits for hashes in original file are on
		'''

		with open(self.lookupper.originalFile,'r') as fin:
			line = fin.readline().strip("\n\r")
			while line != '':

				if not self.lookupper.lookupHashFor(line):
					if self.debug:
						print "Value does not map: " + line
						print "With method: " + self.lookupper.hashMethodName
					return False
				else:
					line = fin.readline().strip("\n")
					continue

		return True


	def randomTest(self):
		'''
			Check with random samples

			Table should be devided 33/66. If it's 50/50 or more, say it's invalid
		'''

		right = 0
		wrong = 0

		i = 0
		while i < 10000:	# take 10k samples
			randstr = ''.join([chr(randint(40,122)) for a in range(30)])

			if self.lookupper.lookupHashFor(randstr):
				right += 1
			else:
				wrong += 1

			i += 1

		if right > 5000:
			return False

		return True

