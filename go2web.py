#!/usr/bin/env python3
import sys
import argparse

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
        print(f"[TODO] fetch URL: {args.u}")

    if args.s:
        term = " ".join(args.s)
        print(f"[TODO] search for: {term}")

if __name__ == "__main__":
    main()
