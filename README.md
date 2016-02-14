# castnow-helpers #

[![Maintained](https://img.shields.io/badge/Maintained-Not%20maintained-red.svg)]()
[![Stable](https://img.shields.io/badge/Status-Unstable-red.svg)]()

Public release: February, 2016

## About ##

Just a bunch of tools to be used with your chromecast using castnow. Download subtitles, crawl kickass for cool stuffs.

## Using ##

First you need to populate the database:

```
$ cd /path/to/castnow-helpers/
$ mkdir -p db front/img/
$ python2 castnow-kickass.py --reset-db
{...}
```

Then you can start the web application:

```
$ cd front
$ php -S 127.0.0.1:8080
```

And visit it with your favorite browser on the address http://127.0.0.1:8080/

## Disclaimer ##

Use at your own risk.
Using of torrents may be illegal in your country.

