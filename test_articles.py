import urllib.request
import re

try:
    req = urllib.request.urlopen('http://localhost:4321/')
    html = req.read().decode('utf-8')
    articles = html.count('<article class="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col"')
    print(f'Homepage: Found {articles} articles in recentPosts list')
except Exception as e:
    print(f'Homepage Error: {e}')

try:
    req = urllib.request.urlopen('http://localhost:4321/blog')
    html = req.read().decode('utf-8')
    articles = html.count('<article')
    print(f'Blog index: Found {articles} articles')
except Exception as e:
    print(f'Blog index Error: {e}')
