""" 
A script to inject Google Analytics into streamlit static files.
"""
import os
import pathlib
import htmlmin
import streamlit as st

from bs4 import BeautifulSoup


STATIC_FILE = pathlib.Path(st.__path__[0]) / "static" / "index.html"

script = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-W6W4DL1THR"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  ga('set', 'anonymizeIp', true);
  gtag('config', '{os.environ["GOOGLE_ANALYTICS_ID"]}');
</script>
"""

with open(STATIC_FILE, "r") as f:
    soup = BeautifulSoup(f, "html.parser")

soup.head.append(BeautifulSoup(script, "html.parser"))

# Write the modified file minified
with open(STATIC_FILE, "w") as f:
    f.write(htmlmin.minify(soup.prettify()))