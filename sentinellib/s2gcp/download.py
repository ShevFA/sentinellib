#!/usr/bin/env python3
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from . import utils

GCP_URL = ('https://storage.googleapis.com/gcp-public-data-sentinel-2/'
           '{dataset}/{utm_zone}/{lat_band}/{grid_square}/{product_id}.SAFE/')

class GCP:
    def __init__(self):
        self.entrypoint = GCP_URL
        self.datasets = {
            'MSIL1C': 'tiles',
            'MSIL2A': 'L2/tiles',
        }

    def _get_structure(self, manifest_file):
        tree = ET.parse(manifest_file)
        root = tree.getroot()
        files = root.findall('.//fileLocation')
        paths = [file.get('href').lstrip('./') for file in files]
        return paths

    def download(self, product_id, out_dir='.', files=None, progressbar=False):
        meta = utils.meta_from_pid(product_id)
        product_type = meta['product_type']
        meta.update({'dataset': self.datasets.get(product_type)})
        meta.update(utils.tile_to_mgrs(meta['tile']))
        base_url = GCP_URL.format(**meta)

        work_dir = Path(out_dir).joinpath(f'{product_id}.SAFE')
        if work_dir.exists():
            return work_dir
        work_dir = work_dir.with_suffix('.SAFE.temp')
        work_dir.mkdir(exist_ok=True)

        manifest_url = base_url + 'manifest.safe'
        manifest_file = utils.download(manifest_url, out_dir=work_dir,
                                       progressbar=progressbar, checksum=True)

        paths = self._get_structure(manifest_file)
        if files is None:
            extra_files = Path(__file__).parent.joinpath('files.json')
            with open(extra_files) as f:
                files = json.load(f).get(product_type)
                paths.extend(files.get('include'))  # files that are not listed in manifest.safe
                for file in files.get('exclude'):  # files listed there, but not in Google Cloud
                    paths.remove(file)
        else:
            def _mk_filter(files):
                def _is_selected(path):
                    for file in files:
                        if file in path:
                            return True
                    return False
                return _is_selected
            paths = list(filter(_mk_filter(files), paths))

        urls = [base_url + path for path in paths]
        dirs = [work_dir.joinpath(Path(path).parent) for path in paths]
        for url, sub_dir in (zip(urls, dirs)):
            sub_dir.mkdir(exist_ok=True, parents=True)
            utils.download(url, out_dir=sub_dir, progressbar=progressbar, checksum=True)
        work_dir.rename(work_dir.with_suffix(''))
        work_dir = work_dir.with_suffix('')
        return work_dir
