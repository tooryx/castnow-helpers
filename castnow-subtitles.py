#! /usr/bin/python

# This script helps castnow by downloading subtitles automatically.
#    To do so, it uses the magnet link.
# This script could be added to firefox to handle magnet-link directly.

import sys
import re
import os
import urllib2
import zipfile

from bs4 import BeautifulSoup

if len(sys.argv) < 2:
	print "./this magnet-link"
	exit(1)

MAGNET = sys.argv[1]
OPTS = sys.argv[2] if len(sys.argv) >= 3 else ""
HOST = "http://www.sub-titles.net"
TMPDIR = "/tmp/"
TMPFILE = "%s/tmp-sub-castnowhelper.zip" % (TMPDIR)
SCORE_NAME = ""

def computeSrtSearchLink(fileName):
	return ("%s/fr/ppodnapisi/search?tbsl=1&asdp=0&sK=%s&sM=0&sJ=2&submit=Rechercher&sAKA=1&sY=&sR=" % (HOST, fileName))

def magnetLinkToFileName(magnetLink):
	magnetSplit = magnetLink.split("&")
	name = ""

	for split in magnetSplit:
		if split[:3] == "dn=":
			name = split[3:]
			break

	SCORE_NAME = name.split('+')
	r = re.search(r"(.+)\+(%28)?(?P<year>[0-9]{4})(%29)?\+", name)
	name = r.group(1) + "+(" + r.group("year") + ")"

	print "Downloading subtitles for: %s" % (name)

	return (SCORE_NAME, name)

def retrieveSiteHTMLSource(downloadLink):
	return (urllib2.urlopen(downloadLink).read())

def parseSrcInfoLinks(sourceHTML):
	soup = BeautifulSoup(sourceHTML)
	result = soup.select('.list .a')

	current_best_sub = ""
	current_best_score = 0

	for sub in result:
		title = sub.select("span[title]")[0].__str__()
		dlLink = sub.select('a[href*="/podnapis/i/"]')[0]
		tags = re.search('title="(.+)">', title).group(1)

		current_score = 0

		for tag in tags.split("."):
			if tag in SCORE_NAME:
				current_score += 1

		if current_score > current_best_score:
			current_best_sub = dlLink

	return current_best_sub

def parseSrcForPredownloadLink(sourceHTML):
	soup = BeautifulSoup(sourceHTML)
	result = soup.select(".box a")
	return result

def downloadSubtitles(linkToSubtitles):
	href = re.search(r'href="(.+)">', linkToSubtitles.__str__())
	src = retrieveSiteHTMLSource(HOST + href.group(1))
	resultSrt = ""

	srcPreDownloadLink = parseSrcForPredownloadLink(src).__str__()
	preDownloadLink = re.search(r'href="([^"]+)"', srcPreDownloadLink).group(1)
	downloadLink = re.sub("/predownload/", "/download/", preDownloadLink)

	retrieveSiteHTMLSource(HOST + preDownloadLink)
	download = retrieveSiteHTMLSource(HOST + downloadLink)

	with open(TMPFILE, "w") as f:
		f.write(download)

	zfile = zipfile.ZipFile(TMPFILE)

	for fileName in zfile.namelist():
		if fileName[-4:] == ".srt":
			zfile.extract(fileName, TMPDIR)
			resultSrt = fileName

	os.unlink(TMPFILE)

	return resultSrt

sub = ""


try:
        SCORE_NAME, downloadName = magnetLinkToFileName(MAGNET)
        searchLink = computeSrtSearchLink(downloadName)
        searchSource = retrieveSiteHTMLSource(searchLink)
        subInfoLink  = parseSrcInfoLinks(searchSource)

        if subInfoLink:
                sub = downloadSubtitles(subInfoLink)
except Exception as e:
        print e

