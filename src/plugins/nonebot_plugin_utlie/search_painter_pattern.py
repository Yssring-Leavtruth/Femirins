import re

search_painter_pattern = re.compile(r'<li class="user-recommendation-item"><a href="/users/(?P<id>.*?)".*?title="(?P<painter>.*?)".*?data-src="(?P<avatar>.*?)".*?>.*?<dd><a href="/users/.*?/artworks".*?>(?P<works>.*?)</a>')