#! /usr/bin/python

from modules.KickassParser import KickassParser
from modules.Database import Database

conf = { "dbpath": "db/database.sqlite" }
database = Database(conf)

ka = KickassParser(database)
ka.retrieveMovieList()

database.close()
