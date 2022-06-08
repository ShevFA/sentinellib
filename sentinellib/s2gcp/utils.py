#!/usr/bin/env python3
import hashlib
import os
from datetime import datetime
from pathlib import Path
import requests

def meta_from_pid(product_id):
    """https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/naming-convention"""
    parts = product_id.split('_')
    return {
        'product_id': product_id,
        'mission': parts[0],
        'product_type': parts[1],
        'acquisition_date': datetime.strptime(parts[2], '%Y%m%dT%H%M%S'),
        'processing_baseline': parts[3].lstrip('N'),
        'orbit': int(parts[4].lstrip('R')),
        'tile': parts[5].lstrip('T'),
        'processing_date': datetime.strptime(parts[6], '%Y%m%dT%H%M%S'),
    }

def tile_to_mgrs(tile):
    """https://en.wikipedia.org/wiki/Military_Grid_Reference_System"""
    return {
        'utm_zone': tile[:2],
        'lat_band': tile[2],
        'grid_square': tile[3:],
    }

def compute_md5(inp_file):
    """Get hexadecimal MD5 hash of a file."""
    with open(inp_file, 'rb') as f:
        h = hashlib.md5(f.read())
    return h.hexdigest()

def download(url, out_dir='.', checksum=False):
    out_name = url.split('/')[-1]
    out_file = Path(out_dir).joinpath(out_name)
    
    r = requests.get(url, stream=True)
    filesize = int(r.headers.get('Content-Length', 0))
    etag = r.headers.get('ETag', '').replace('"', '')

    if r.status_code != 200:
        raise requests.exceptions.HTTPError(str(r.status_code))

    if os.path.isfile(out_file) and os.path.getsize(out_file) == filesize:
        return out_file

    with open(out_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024**2):
            if chunk: f.write(chunk)
    r.close()

    if checksum:
        if not compute_md5(out_file) == etag:
            raise requests.exceptions.HTTPError('Download corrupted.')

    return out_file