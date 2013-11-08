#!/usr/bin/env python
#
# Handkerchief: A GitHub Issues offline reader
#
# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import requests
import json
from string import Template
from codecs import open

html_template = """
<html>
	<head>
		<meta charset="utf-8"/>
		<script type="text/javascript">
			content = $content;
			console.log(content);
			function reload_content(id){
				for(var i in content){
					console.log(content[i],id);
					if(content[i]["number"] == id){
						document.getElementById("content").firstChild.nodeValue = content[i]["body"];
						break;
					}
				}
			}
		</script>
		<style>
			div#menu { width:400px; position:absolute; font-size:small;}
			div#content { width:400px; position:absolute; left:400px;}
		</style>
	</head>
	<body>
		<div>
			<div id = "menu">
				<ul>
				$menulinks
				</ul>
			</div>
			<div id = "content">
			</div>
		</div>
	</body>
</html>
"""

r = requests.get('https://api.github.com/repos/%s/issues?state=open&filter=all' % sys.argv[1])
if r.ok:
	data = {}
	data["content"] = r.text or r.content
	issues = json.loads(data["content"])

	menulinks = []
	for issue in issues:
		nr = int(issue["number"])
		menulinks.append("""<li><a href="javascript:reload_content('%d')">#%d: %s</a></li>""" % (nr,nr,issue["title"]))
	data["menulinks"] = "\n".join(menulinks)

	fid = open("tissues.html","w","utf8")
	fid.write(Template(html_template).substitute(data))
	fid.close()
else:
	print r
