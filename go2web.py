#!/usr/bin/env python3
import sys
import argparse
import socket
import ssl
import json
import hashlib
import os
import time
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".go2web_cache")
CACHE_TTL = 300

def cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()

def cache_get(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, cache_key(url))
    if os.path.exists(path):
        if time.time() - os.path.getmtime(path) < CACHE_TTL:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
    return None

def cache_set(url, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, cache_key(url))
    with open(path, "w", encoding="utf-8", errors="replace") as f:
        f.write(data)

def decode_chunked(data):
    result = b""
    while data:
        crlf = data.find(b"\r\n")
        if crlf == -1:
            break
        size = int(data[:crlf].split(b";")[0], 16)
        if size == 0:
            break
        chunk = data[crlf + 2: crlf + 2 + size]
        result += chunk
        data = data[crlf + 2 + size + 2:]
    return result

def raw_http_request(url, accept="text/html,application/json"):
    parsed = urlparse(url)
    scheme = parsed.scheme
    host = parsed.hostname
    port = parsed.port or (443 if scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Accept: {accept}\r\n"
        f"Accept-Language: en-US,en;q=0.9\r\n"
        f"User-Agent: go2web/1.0\r\n"
        f"Connection: close\r\n\r\n"
    )

    sock = socket.create_connection((host, port), timeout=10)
    if scheme == "https":
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)

    sock.sendall(request.encode())

    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    sock.close()

    header_end = response.find(b"\r\n\r\n")
    headers_raw = response[:header_end].decode("utf-8", errors="replace")
    body_raw = response[header_end + 4:]

    status_line = headers_raw.splitlines()[0]
    status_code = int(status_line.split()[1])

    headers = {}
    for line in headers_raw.splitlines()[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    if headers.get("transfer-encoding", "").lower() == "chunked":
        body_raw = decode_chunked(body_raw)

    try:
        body = body_raw.decode("utf-8", errors="replace")
    except Exception:
        body = body_raw.decode("latin-1", errors="replace")

    return status_code, headers, body

def http_get(url, accept="text/html,application/json", max_redirects=5):
    cached = cache_get(url)
    if cached:
        print("[cache hit]")
        return cached, "text/html"

    for _ in range(max_redirects):
        status, headers, body = raw_http_request(url, accept)
        if status in (301, 302, 303, 307, 308):
            location = headers.get("location", "")
            if location.startswith("/"):
                parsed = urlparse(url)
                url = f"{parsed.scheme}://{parsed.hostname}{location}"
            else:
                url = location
            print(f"[redirect → {url}]")
            continue
        content_type = headers.get("content-type", "text/html")
        cache_set(url, body)
        return body, content_type
    raise Exception("Too many redirects")

def render_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)

def render_response(body, content_type):
    if "json" in content_type:
        try:
            data = json.loads(body)
            return json.dumps(data, indent=2)
        except Exception:
            return body
    else:
        return render_html(body)

def search(term):
    query = quote_plus(term)
    url = f"https://html.duckduckgo.com/html/?q={query}"
    body, content_type = http_get(url, accept="text/html")
    soup = BeautifulSoup(body, "html.parser")

    results = []
    for result in soup.select(".result"):
        title_tag = result.select_one(".result__title")
        link_tag = result.select_one(".result__url")
        snippet_tag = result.select_one(".result__snippet")

        title = title_tag.get_text(strip=True) if title_tag else "No title"
        link = link_tag.get_text(strip=True) if link_tag else ""
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        if title and link:
            results.append((title, link, snippet))
        if len(results) >= 10:
            break

    return results

def main():
    parser = argparse.ArgumentParser(prog="go2web", add_help=False)
    parser.add_argument("-u", metavar="URL", help="Make HTTP request to URL")
    parser.add_argument("-s", metavar="SEARCH_TERM", nargs="+", help="Search term")
    parser.add_argument("-h", action="store_true", help="Show help")

    args = parser.parse_args()

    if args.h or (not args.u and not args.s):
        print("""go2web - HTTP over TCP sockets

Usage:
  go2web -u <URL>          Make an HTTP request and print human-readable response
  go2web -s <search-term>  Search and print top 10 results
  go2web -h                Show this help""")
        sys.exit(0)

    if args.u:
        try:
            body, content_type = http_get(args.u)
            print(render_response(body, content_type))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if args.s:
        term = " ".join(args.s)
        try:
            results = search(term)
            if not results:
                print("No results found.")
            else:
                for i, (title, link, snippet) in enumerate(results, 1):
                    print(f"{i}. {title}")
                    print(f"   {link}")
                    if snippet:
                        print(f"   {snippet}")
                    print()

                print("Enter result number to open (or press Enter to skip): ", end="")
                choice = input().strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        link = results[idx][1]
                        if not link.startswith("http"):
                            link = "https://" + link
                        body, content_type = http_get(link)
                        print(render_response(body, content_type))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
