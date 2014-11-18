#! /usr/bin/python

import sys

from modules.KickassParser import KickassParser
from modules.Database import Database

RESET_DB = False

for element in sys.argv:
	if element == "--reset-db":
		RESET_DB = True


conf = { "dbpath": "db/database.sqlite" }
database = Database(conf)

if RESET_DB:
	print "[+] Reseting db...	"
	database.reset()

ka = KickassParser(database)
ka.retrieveMovieList()

database.close()
