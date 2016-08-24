import bloomhash
import hashlib

wordlist = "Super_mega_dic.txt"

# create table (takes a while)
lookbuilder = bloomhash.bloomhashLookupBuilder(wordlist)
lookbuilder.addHashMethod(hashlib.sha1)
#lookbuilder.addHashMethod(hashlib.sha224)
lookbuilder.addHashMethod(hashlib.sha256)
#lookbuilder.addHashMethod(hashlib.sha384)
lookbuilder.addHashMethod(hashlib.sha512)
lookbuilder.addHashMethod(hashlib.md5)
lookbuilder.processFile()


# check table for validity
lookupperTest = bloomhash.bloomhashLookupTester(wordlist + ".bloomhash.openssl_md5.dat.size")
if not lookupperTest.checkTable():
	print "md5 table is corrupt"
else:
	print "md5 table is valid"


# use the table for lookups
# prints false positives about 1/3'rd of the time
# negative results mean the word can not be in the table
lookupper = bloomhash.bloomhashLookupper(wordlist + ".bloomhash.openssl_md5.dat.size")

testPassesCorrect = ["welkom","test"]
for testpass in testPassesCorrect:
	print "Must be correct: " + str(lookupper.lookupHashFor(testpass))

testPassesWrong = ["Foobartest1234","Nonexistingpasswordinlist","Alsonotinwordlist","Alsonotinwordlist2","Alsonotinwordlist3","Alsonotinwordlist4","Alsonotinwordlist5","Alsonotinwordlist6"]
for testpass in testPassesWrong:
	print "Not in list lookup: " + str(lookupper.lookupHashFor(testpass))
	