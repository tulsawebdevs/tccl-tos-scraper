tccl-tos-scraper
================

Scraper for [Tulsa City-County Library's Tulsa Organizations &amp; Services][tccl-tos]
data

With the objective to load it into [TulsaWiki][] via API

[tccl-tos]: http://opac.tulsalibrary.org:82/
[TulsaWiki]: http://tulsawiki.org/

Getting Started
---------------

Make a virtualenv

Install the requirements

    pip install -r requirements.txt

Create a cache/ dir

    mkdir cache

Run it

    python scrape.py
