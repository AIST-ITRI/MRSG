#! /usr/bin/python

import sys
import warc
import gzip

def main():
    files = sys.argv[1:]

    for file in files:
        f = warc.WARCFile(fileobj=gzip.open(file))
        try:
            n = 0
            for record in f:
                if record['Content-Type'] == 'application/http; msgtype=response':
                    url = record['WARC-Target-URI']
                    payload = record.payload.read()
                    headers, body = payload.split('\r\n\r\n', 1)
                    if 'Content-Type: text/html' in headers:
                        print('%s * * * *' % body)
                        print(url)
        finally:
            f.close()

if __name__ == '__main__':
    sys.exit(main())
