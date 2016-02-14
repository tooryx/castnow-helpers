import urllib2
import re

from bs4 import BeautifulSoup

class ImdbParser:

	def __init__(self):
		self._host_base = "http://www.imdb.com"
		self._titleUrl_base = self._host_base + "/title/tt"

	def _getMethod(self, url):
		request = urllib2.Request(url)
		request.add_header("Accept-Language", "en,en-us;q=0.5")
		response = urllib2.urlopen(request, timeout=5)
		data = response.read()

		return data

	def retrieveMovieInfo(self, movieId):
		imdb_info = {}

		pageSrc = self._getMethod(self._titleUrl_base + movieId + "/")
		soup = BeautifulSoup(pageSrc, "lxml")

		imdb_info["name"] = soup.select('h1[itemprop="name"]')[0].contents[0]
		imdb_info["date"] = soup.select('meta[itemprop="datePublished"]')[0]["content"]
		imdb_info["year"] = re.search("([0-9]{4})", imdb_info["date"]).group(1)
		imdb_info["rating"] = float(soup.select('span[itemprop="ratingValue"]')[0].contents[0].strip())
		imdb_info["summary"] = soup.select('div[itemprop="description"]')[0].contents[0].strip()
		imdb_info["picture"] = soup.select('img[itemprop="image"]')[0]["src"]

		return imdb_info
