# go2web

A command-line HTTP client built on raw TCP sockets — no HTTP libraries used.

## Usage
```
go2web -u <URL>         # fetch a URL and print human-readable response
go2web -s <search-term> # search DuckDuckGo and print top 10 results
go2web -h               # show help
```

## Demo

![demo](demo.gif)

## Features

- Raw TCP sockets for all HTTP/HTTPS traffic
- HTTP redirect following (301, 302, 303, 307, 308)
- Human-readable output (HTML tags stripped)
- JSON and HTML content negotiation
- File-based cache with 5 minute TTL
- Open search results directly from the CLI
