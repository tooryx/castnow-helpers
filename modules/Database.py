import sqlite3

class Database:

	def __init__(self, conf):
		self._db_conn = sqlite3.connect(conf["dbpath"])
		self._db = self._db_conn.cursor()

	def close(self):
		self._db_conn.close()

	def alreadyVisited(self, tracker, link):
		res = self._db.execute("SELECT url FROM visited WHERE tracker=? AND url=?", (tracker, link,))
		return (len(res.fetchall()) >= 1)

	def isMovieInDB(self, movieObject):
		name = movieObject.movieName
		year = movieObject.movieYear

		res = self._db.execute("SELECT id FROM movie WHERE name=? and year=?", (name, year,))

		return (len(res.fetchall()) >= 1)

	def addMovie(self, movieObject):
		name = movieObject.movieName
		year = movieObject.movieYear
		picture = movieObject.pictureLink
		magnet = movieObject.magnetLink
		quality = movieObject.quality

		self._db.execute("INSERT INTO movie(name, year, picture, magnet, quality) \
						  VALUES(?, ?, ?, ?, ?)", (name, year, picture, magnet, quality,))
		self._db_conn.commit()

	def visited(self, tracker, link):
		self._db.execute("INSERT INTO visited VALUES(?, ?)", (tracker, link,))
		self._db_conn.commit()
