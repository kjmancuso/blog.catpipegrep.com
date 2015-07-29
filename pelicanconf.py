#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Kevin Mancuso'
SITENAME = u'cat | grep'
SITEURL = 'http://blog.catpipegrep.com'
RELATIVE_URLS = False

PATH = 'content'

TIMEZONE = 'America/Chicago'

# Theme info
DEFAULT_LANG = u'en'
THEME = 'themes/pelican-bootstrap3'
BOOTSTRAP_THEME = 'slate'
HIDE_SIDEBAR = True
TYPOGRIFY = True
SUMMARY_MAX_LENGTH = None
DEFAULT_PAGINATION = 5
DISPLAY_BREADCRUMBS = False
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_ARTICLE_INFO_ON_INDEX = True
MENUITEMS = [('About', '/pages/about.html')]

# Paths for clean URLs
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

# Plugins
PLUGIN_PATHS = ['plugins']
PLUGINS = ['sitemap', 'social', 'pelican_fontawesome']

# Disable unused elements
AUTHOR_SAVE_AS = ''
CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
DIRECT_TEMPLATES = (('index', 'archives', 'search'))

# Paths
STATIC_PATHS = ['images', 'extra/favicon.ico']
EXTRA_PATH_METADATA = {
        'extra/favicon.ico': {'path': 'extra/favicon.ico'},
}
FAVICON = 'extra/favicon.ico'

# Feed generation is usually not desired when developing
FEED_DOMAIN = 'http://blog.catpipegrep.com'
FEED_ALL_ATOM = 'atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# External utils
DISQUS_SITENAME = 'catpipegrep'
GOOGLE_ANALYTICS = 'UA-47947008-1'

# Sitemap
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.8,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'weekly',
        'indexes': 'daily',
        'pages': 'weekly'
    }
}
