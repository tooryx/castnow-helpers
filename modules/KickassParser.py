import urllib2
import gzip
import re

from Movie import Movie
from StringIO import StringIO
from bs4 import BeautifulSoup

class KickassParser:
	def __init__(self, database):
		self._db = database
		self._movieListBaseUrl = "http://kickass.to"
		self._numberOfPages = 20

	def _getRequest(self, url):
		request = urllib2.Request(url)
		request.add_header('Accept-encoding', 'gzip')
		response = urllib2.urlopen(request)

		data = response.read()

		if response.info().get('Content-Encoding') == 'gzip':
		    buf = StringIO(data)
		    f = gzip.GzipFile(fileobj=buf)
		    data = f.read()

		return data

	def _getMovieList(self):
		movie_list = []

		for i in range(1, self._numberOfPages + 1, 1):
			downloadLink = self._movieListBaseUrl + "/movies/%s/" % (i)
			pageSrc = self._getRequest(downloadLink)
			parsed = BeautifulSoup(pageSrc)
			links = parsed.find_all("a", class_="cellMainLink")

			movie_list += links

		return movie_list

	def _getMovieInfo(self, linkMovieBox):
		movieInfoPageSrc = self._getRequest(self._movieListBaseUrl + linkMovieBox)
		soup = BeautifulSoup(movieInfoPageSrc)
		result = {}

		infos = soup.find_all("div", class_="dataList")

		if not(infos):
			return

		infos = infos[0]

		name = infos.ul.li.a.span.contents
		result["name"] = name[0].__str__()

		seeders = soup.select('strong[itemprop="seeders"]')[0].contents[0]
		result["seeders"] = int(seeders)

		quality = soup.select('span[id^="quality_"]')[0].contents[0]
		result["quality"] = quality

		cover = soup.find_all("a", class_="movieCover")[0].img['src']
		result["picture"] = cover

		magnet = soup.find_all("a", class_="magnetlinkButton")[0]['href']
		result["magnet"] = magnet

		# FIXME
		year = infos.find_all("ul")[1].find_all("li")[1].strong.nextSibling
		year = re.search("([0-9]{4})", year)

		if year:
			result["year"] = int(year.group(1))
		else:
			result["year"] = 0000

		return result


	def _buildMovieObj(self, movieInfo):
		# FIXME: More fields possibly
		movie = Movie(movieInfo["name"])
		movie.movieYear = movieInfo["year"]
		movie.pictureLink = movieInfo["picture"]
		movie.magnetLink = movieInfo["magnet"]
		movie.quality = movieInfo["quality"]
		movie.seeders = movieInfo["seeders"]

		return movie

	def retrieveMovieList(self):
		movies = self._getMovieList()
		moviesObjects = []

		for movie in movies:
			linkMovieBox = movie['href']

			try:
				if not self._db.alreadyVisited("kickass", linkMovieBox):
					self._db.visited("kickass", linkMovieBox)
					movieInfo = self._getMovieInfo(linkMovieBox)

					if not(movieInfo):
						continue

					movieObj = self._buildMovieObj(movieInfo)

					if not self._db.isMovieInDB(movieObj) \
					and movieObj.quality in [ "720p", "1080p" ]:
						self._db.addMovie(movieObj)
						moviesObjects.append(movieObj)
			except:
				print "Error while processing: %s" % (linkMovieBox)

		return moviesObjects