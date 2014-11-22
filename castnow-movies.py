#! /usr/bin/python

import sys

from modules.KickassParser import KickassParser
from modules.Database import Database

RESET_DB = False
RESET_VISITED = False

if "--reset-db" in sys.argv:
	RESET_DB = True
elif "--reset-visited" in sys.argv:
	RESET_VISITED = True


conf = { "dbpath": "db/database.sqlite" }
database = Database(conf)

if RESET_DB:
	print "[+] Reseting db..."
	database.reset()
elif RESET_VISITED:
	print "[+] Reseting list of visited links..."
	database.reset_visited()


ka = KickassParser(database)
ka.retrieveMovieList()

database.close()
