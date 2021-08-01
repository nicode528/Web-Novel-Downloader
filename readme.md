# Chinese Web Novel Downloader

### Requirements

Python 3.7 and above

### Installing

```
pip3 install -r requirements.txt
```

### How to use
```
Usage: main.py [OPTIONS]

  Download web novels as epub

Options:
  -u, --url TEXT         book url, check readme.md for available sites and url
                         formats
  -o, --output-dir TEXT  output directory
  --help                 Show this message and exit.
```
eg: `python main.py -u https://www.xxbiquge.net/75_75922/`

Currently accepts URLs from
```
https://www.xxbiquge.net
    eg: https://www.xxbiquge.net/75_75922/

https://www.xbiquge.so
    eg: https://www.xbiquge.so/book/33903/

https://www.hetushu.com
    eg: https://www.hetushu.com/book/2904/index.html
```

### Development

#### Adding new sites

Add a new concrete class for `SiteInterface` in `./sitemanager`