import urllib2
import gzip
import re

from Movie import Movie
from ImdbParser import ImdbParser
from StringIO import StringIO
from bs4 import BeautifulSoup

class KickassParser:
	def __init__(self, database):
		self._db = database
		self._host_base = "http://kickass.to"
		self._numberOfPages = 20
		self._imdbParser = ImdbParser()

	def _getMethod(self, url):
		request = urllib2.Request(url)
		request.add_header('Accept-encoding', 'gzip')

		for i in range(3):
			try:
				response = urllib2.urlopen(request, timeout=2)
				break
			except:
				continue

		data = response.read()

		if response.info().get('Content-Encoding') == 'gzip':
		    buf = StringIO(data)
		    f = gzip.GzipFile(fileobj=buf)
		    data = f.read()

		return data

	def _getMovieList(self):
		movie_list = []

		for i in range(1, self._numberOfPages + 1, 1):
			print "[-] Parsing page [ %i / %i ]" % (i, self._numberOfPages)
			downloadLink = self._host_base + "/movies/%s/" % (i)
			pageSrc = self._getMethod(downloadLink)
			parsed = BeautifulSoup(pageSrc, "lxml")
			links = parsed.find_all("a", class_="cellMainLink")

			movie_list += links

		return movie_list

	def _getMovieInfo(self, directLink):
		movieInfoPageSrc = self._getMethod(directLink)
		soup = BeautifulSoup(movieInfoPageSrc, "lxml")
		result = {}

		infos = soup.find_all("div", class_="dataList")[0]

		imdb = soup.select("a[href^=http://www.imdb.com]")[0].contents[0]
		result["imdb"] = imdb


		seeders = soup.select('strong[itemprop="seeders"]')[0].contents[0]
		result["seeders"] = int(seeders)

		quality = soup.select('span[id^="quality_"]')[0].contents[0]
		result["quality"] = quality

		magnet = soup.find_all("a", class_="kaGiantButton")[2]['href']
		result["magnet"] = magnet

		pic = soup.find_all("a", class_="movieCover")[0].contents[0]["src"]
		img_file = urllib2.urlopen("http:%s" % (pic))

		pic_name = pic.split("/")[-1]

		with open("front/img/%s" % (pic_name), "w") as f:
			f.write(img_file.read())

		result["picture"] = pic_name

		# At this point, if there's no IMDB link, an exception should have been raised.
		imdb_info = self._imdbParser.retrieveMovieInfo(imdb)

		result["name"] = imdb_info["name"]
		result["year"] = imdb_info["year"]
		result["rating"] = imdb_info["rating"]
		result["summary"] = imdb_info["summary"]

		return result

	def _buildMovieObj(self, movieInfo):
		movie = Movie(movieInfo["name"])
		movie.movieYear = movieInfo["year"]
		movie.pictureLink = movieInfo["picture"]
		movie.magnetLink = movieInfo["magnet"]
		movie.quality = movieInfo["quality"]
		movie.seeders = movieInfo["seeders"]
		movie.imdb = movieInfo["imdb"]
		movie.ranking = movieInfo["rating"]
		movie.summary = movieInfo["summary"]

		return movie

	def _processMovieInformations(self, directLink, isSameMovie=False):
		print "[-] Processing: %s" % (directLink)
		self._db.visited(directLink)
		movieInfo = self._getMovieInfo(directLink)
		movieObj = self._buildMovieObj(movieInfo)

		movieObj.visitLink = directLink

		if movieObj.quality == "Unknown":
			if "720p" in directLink:
				movieObj.quality = "unknown-720p"
			elif "1080p" in directLink:
				movieObj.quality = "unkown-1080p"

		if not self._db.isMovieInDB(movieObj):
			self._db.addMovie(movieObj)
		elif self._db.isBetterQuality(movieObj) \
		or isSameMovie:
			self._db.updateMovie(movieObj)

	def retrieveMovieList(self):
		movies = self._getMovieList()

		for movie in movies:
			linkMovieBox = movie['href']
			directLink = self._host_base + linkMovieBox

			try:
				if not self._db.alreadyVisited(directLink):
					self._processMovieInformations(directLink)
				elif self._db.linkIsRelatedToMovie(directLink):
					self._processMovieInformations(directLink, isSameMovie=True)
			except Exception as e:
				print "[-][\033[31;01mERR\033[00m] Processing: %s (%s)" % (directLink, e)
