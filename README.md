# go2web

A command-line HTTP client built on raw TCP sockets — no HTTP libraries used. Built for the Web Programming Lab 5 assignment.

## Requirements

- Python 3.x
- beautifulsoup4 (`pip3 install beautifulsoup4`)

## Installation
```bash
git clone https://github.com/diana7376/go2web
cd go2web
pip3 install beautifulsoup4
chmod +x go2web
```

## Usage
```
go2web -u <URL>         # make an HTTP request to the specified URL and print the response
go2web -s <search-term> # search DuckDuckGo and print top 10 results
go2web -h               # show this help
```

## Examples
```bash
# Fetch a webpage
./go2web -u http://example.com

# Fetch a JSON response
./go2web -u https://httpbin.org/get

# Search for a term
./go2web -s python sockets

# Multi-word search
./go2web -s what is TCP

# Open a search result (enter a number when prompted)
./go2web -s python sockets
> Enter result number to open: 1
```

## Features

### Core
- Raw TCP sockets for all HTTP and HTTPS traffic — no requests library or urllib
- Human-readable output — all HTML tags are stripped, only text is shown
- Supports both HTTP and HTTPS (port 80 and 443)

### Extra
- **HTTP redirects** — automatically follows 301, 302, 303, 307, 308 redirects
- **Cache** — responses are cached to disk for 5 minutes, repeated requests return instantly with `[cache hit]`
- **Content negotiation** — detects `Content-Type` header and pretty-prints JSON or strips HTML accordingly
- **Open search results** — after searching, type a result number to fetch and read that page directly

## How it works

1. The URL is parsed into host, port, path and scheme
2. A raw TCP socket is opened to the server
3. If HTTPS, the socket is wrapped in TLS/SSL
4. An HTTP/1.1 GET request is manually built as a string and sent as bytes
5. The response bytes are read in chunks and split into headers and body
6. If the status code is a redirect, the Location header is followed automatically
7. The response body is checked for chunked transfer encoding and decoded if needed
8. BeautifulSoup strips all HTML tags and returns clean readable text
9. The response is saved to disk cache before being printed

## Cache

Responses are cached in `~/.go2web_cache/` as files named by MD5 hash of the URL. Cache expires after 5 minutes. Run the same URL twice to see it in action:
```bash
./go2web -u http://example.com   # fetches from network
./go2web -u http://example.com   # returns [cache hit]
```

## Demo

![demo](Usage%20Go2Web.gif)
