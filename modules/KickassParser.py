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

		infos = soup.find_all("div", class_="dataList")[0]

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
			print "[-] Processing: %s" % (linkMovieBox)

			try:
				if not self._db.alreadyVisited("kickass", linkMovieBox):
					self._db.visited("kickass", linkMovieBox)
					movieInfo = self._getMovieInfo(linkMovieBox)
					movieObj = self._buildMovieObj(movieInfo)

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