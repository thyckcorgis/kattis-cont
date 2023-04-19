#!/usr/bin/env python3

from subprocess import check_output
# Paste cURL command here surrounded by double quotes
curl = ""

a = curl.split(' ')
# response is gzipped so we tell cURL to decompress it first
cmd = ' '.join(a[:1] + ['--compressed'] + a[1:])
with open('page.html', 'wb') as f:
    f.write(check_output(cmd, shell=True))
