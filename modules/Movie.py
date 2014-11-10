class Movie:

	movieName = ""
	movieYear = 0000
	summary = ""
	pictureLink = ""
	magnetLink = ""
	seeders = 0

	visitLink = ""

	imdbLink = ""
	ranking = 0
	quality = ""

	def __init__(self, movieName):
		self.movieName = movieName
