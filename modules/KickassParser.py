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
			parsed = BeautifulSoup(pageSrc)
			links = parsed.find_all("a", class_="cellMainLink")

			movie_list += links

		return movie_list

	def _getMovieInfo(self, linkMovieBox):
		movieInfoPageSrc = self._getMethod(self._host_base + linkMovieBox)
		soup = BeautifulSoup(movieInfoPageSrc)
		result = {}

		infos = soup.find_all("div", class_="dataList")[0]

		imdb = soup.select("a[href^=http://anonym.to/?http://www.imdb.com]")[0].contents[0]
		result["imdb"] = imdb


		seeders = soup.select('strong[itemprop="seeders"]')[0].contents[0]
		result["seeders"] = int(seeders)

		quality = soup.select('span[id^="quality_"]')[0].contents[0]
		result["quality"] = quality

		magnet = soup.find_all("a", class_="magnetlinkButton")[0]['href']
		result["magnet"] = magnet

		# At this point, if there's no IMDB link, an exception should have been raised.
		imdb_info = self._imdbParser.retrieveMovieInfo(imdb)

		result["name"] = imdb_info["name"]
		result["year"] = imdb_info["year"]
		result["rating"] = imdb_info["rating"]
		result["summary"] = imdb_info["summary"]
		result["picture"] = imdb_info["picture"]

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

	def retrieveMovieList(self):
		movies = self._getMovieList()
		moviesObjects = []

		for movie in movies:
			linkMovieBox = movie['href']
			print "[-] Processing: %s" % (linkMovieBox)

			try:
				if not self._db.alreadyVisited("kickass", linkMovieBox):
					self._db.visited("kickass", linkMovieBox)
					movieInfo = self._getMovieInfo(linkMovieBox)
					movieObj = self._buildMovieObj(movieInfo)

					movieObj.visitLink = self._host_base + linkMovieBox

					if movieObj.quality == "Unknown":
						if "720p" in linkMovieBox:
							movieObj.quality = "720p"
						elif "1080p" in linkMovieBox:
							movieObj.quality = "1080p"

					if not self._db.isMovieInDB(movieObj) \
					and movieObj.quality in [ "720p", "1080p", "HDRiP", "BDRip" ]:
						self._db.addMovie(movieObj)
						moviesObjects.append(movieObj)
			except Exception as e:
				print "[-][\033[31;01mERR\033[00m] Processing: %s (%s)" % (linkMovieBox, e)

		return moviesObjects