import sqlite3

class Database:

	def __init__(self, conf):
		self._db_conn = sqlite3.connect(conf["dbpath"])
		self._db = self._db_conn.cursor()

	def close(self):
		self._db_conn.close()

	def reset(self):
		self._db.execute("DELETE FROM movie")
		self._db.execute("DELETE FROM visited")
		self._db_conn.commit()

	def reset_visited(self):
		self._db.execute("DELETE FROM visited")
		self._db_conn.commit()

	def alreadyVisited(self, link):
		res = self._db.execute("SELECT url FROM visited WHERE url=?", (link,))
		return (len(res.fetchall()) >= 1)

	def _retrieveMovieFromObject(self, movieObject, fields="id"):
		name = movieObject.movieName
		year = movieObject.movieYear

		res = self._db.execute("SELECT %s FROM movie WHERE name=? and year=? LIMIT 1" % (fields), (name, year,))

		return res.fetchall()

	def isMovieInDB(self, movieObject):
		movieArray = self._retrieveMovieFromObject(movieObject)
		return (len(movieArray) >= 1)

	def _calculateMovieQualityScore(self, quality):
		scores = {
			"1080p": 10,
			"720p": 10,
			"unkown-1080p": 9,
			"unkown-720p": 8,
			"MPEG-4": 7,
			"HDRiP": 6,
			"BDRip": 5,
			"Blu-Ray": 4,
			"DVDRip": 3,
			"DVD": 2,
			"Unknown": 1,
			"Screener": 0,
			"TeleSync": 0,
			"Cam": 0
		}

		if quality in scores.keys():
			calculatedScore = scores[quality]
		else:
			calculatedScore = 0

		return calculatedScore

	def isBetterQuality(self, movieObj):
		movie = self._retrieveMovieFromObject(movieObj, fields="quality,seeders")

		inDbQualityScore = self._calculateMovieQualityScore(movie[0][0])
		newComerQualityScore = self._calculateMovieQualityScore(movieObj.quality)

		inDbSeeders = movie[0][1]
		newComerSeeders = movieObj.seeders

		if inDbQualityScore == newComerQualityScore:
			return (inDbSeeders < newComerSeeders)

		return (inDbQualityScore < newComerQualityScore)

	def linkIsRelatedToMovie(self, directLink):
		res = self._db.execute("SELECT id FROM movie WHERE visitLink=? LIMIT 1", (directLink,))
		return (len(res.fetchall()) >= 1)

	def updateMovie(self, movieObj):
		movie = self._retrieveMovieFromObject(movieObj)

		name = movieObj.movieName
		year = movieObj.movieYear

		seeders = movieObj.seeders
		picture = movieObj.pictureLink
		magnet = movieObj.magnetLink
		quality = movieObj.quality
		visitLink = movieObj.visitLink
		rating = movieObj.ranking
		summary = movieObj.summary
		imdb = movieObj.imdb

		self._db.execute("UPDATE movie \
						  	SET seeders = ?, picture = ?, magnet = ?, \
						  		quality = ?, visitLink = ?, ranking = ?, \
						  		summary = ?, imdb = ? \
						  	WHERE name = ? AND year = ?", \
						(seeders,picture,magnet,quality,visitLink,rating,summary,imdb,name,year,))
		self._db_conn.commit()

	def addMovie(self, movieObject):
		name = movieObject.movieName
		year = movieObject.movieYear
		seeders = movieObject.seeders
		picture = movieObject.pictureLink
		magnet = movieObject.magnetLink
		quality = movieObject.quality
		visitLink = movieObject.visitLink
		imdb = movieObject.imdb
		rating = movieObject.ranking
		summary = movieObject.summary

		self._db.execute("INSERT INTO movie(name, seeders, year, picture, magnet, quality, visitLink, imdb, ranking, summary) \
						  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
						(name, seeders, year, picture, magnet, quality, visitLink, imdb, rating, summary,))
		self._db_conn.commit()

	def visited(self, link):
		self._db.execute("INSERT INTO visited VALUES(?)", (link,))
		self._db_conn.commit()
