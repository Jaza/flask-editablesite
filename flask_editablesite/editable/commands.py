import os

try:
    from urllib.parse import urlparse  # python 3.x
except ImportError:
    from urlparse import urlparse  # python 2.x

from flask_script import Command, Option, prompt

from flask_editablesite.editable.sample_images import scrape_sample_images


class DownloadSampleImages(Command):
    """Downloads sample images by scraping a specified URL for links."""

    def get_options(self):
        return (
            Option('--url',
                   help='URL of web site to scrape for images'),
            Option('--targetdir',
                   help='Path to target directory'),
            Option('--parentelname',
                   help='Parent element name (optional)'),
            Option('--parentelclass',
                   help='Parent element class (optional)'),
            Option('--onlyfirstel',
                   help=('Only get the first element of each parent '
                         '(optional)'),
                   default=False),
        )

    def download_sample_images(self, url, targetdir, parentelname,
                               parentelclass, onlyfirstel):
        import requests

        from clint.textui import progress

        hrefs = scrape_sample_images(
            url=url,
            parentelname=parentelname,
            parentelclass=parentelclass,
            onlyfirstel=onlyfirstel)

        target_filepath = os.path.abspath(targetdir)
        if not os.path.exists(target_filepath):
            os.makedirs(target_filepath)

        total_downloaded = 0

        for href in progress.bar(hrefs):
            filename = os.path.basename(urlparse(href).path)
            filepath = os.path.join(target_filepath, filename)

            if not os.path.exists(filepath):
                r = requests.get(href, stream=True)

                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                total_downloaded += 1

        return 'Downloaded %d images' % total_downloaded

    def run(self, url=None, targetdir=None, parentelname=None,
            parentelclass=None, onlyfirstel=False):
        if not url:
            url = prompt("URL of web site to scrape for images")

        if not targetdir:
            targetdir = prompt("Path to target directory")

        msg = self.download_sample_images(
            url=url,
            targetdir=targetdir,
            parentelname=parentelname,
            parentelclass=parentelclass,
            onlyfirstel=onlyfirstel)

        if not msg:
            msg = "Error downloading images"

        print(msg)
