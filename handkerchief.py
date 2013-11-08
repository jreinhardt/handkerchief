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
			issue_data = $issue_data;
			comment_data = $comment_data;
			function reload_content(id){
				for(var i = 0; i < issue_data.length; i++){
					if(issue_data[i]["number"] == id){
						document.getElementById("content").firstChild.nodeValue = issue_data[i]["body"];
						var comment_node = document.getElementById("comments");
						while (comment_node.hasChildNodes()) {
							comment_node.removeChild(comment_node.lastChild);
						}
						for(var j = 0; j < comment_data.length; j++){
							if(comment_data[j]["issue_url"] == issue_data[i]["url"]){
								var comment = document.createElement("div");
								comment.appendChild(document.createTextNode(comment_data[j]["body"]));
								comment_node.appendChild(comment);
							}
						}
						break;
					}
				}
			}
		</script>
		<style>
			div#wrapper { width: 100%, min-width:800; position:relative;}
			div#menu { width:40%; position:absolute; left:0; font-size:small;}
			div#col_right { width:60%; position:absolute; right:0;}
		</style>
	</head>
	<body>
		<div id="wrapper">
			<div id = "menu">
				<ul>
				$menulinks
				</ul>
			</div>
			<div id = "col_right">
				<div id = "content">
				</div>
				<div id = "comments">
				</div>
			</div>
		</div>
	</body>
</html>
"""

issue_request = requests.get('https://api.github.com/repos/%s/issues?state=open&filter=all&direction=asc' % sys.argv[1])
comment_request = requests.get('https://api.github.com/repos/%s/issues/comments' % sys.argv[1])
if issue_request.ok and comment_request.ok:
	data = {}
	data["issue_data"] = issue_request.text or issue_request.content
	data["comment_data"] = comment_request.text or comment_request.content

	menulinks = []
	for issue in json.loads(data["issue_data"]):
		nr = int(issue["number"])
		menulinks.append("""<li><a href="javascript:reload_content('%d')">#%d: %s</a></li>""" % (nr,nr,issue["title"]))
	data["menulinks"] = "\n".join(menulinks)

	fid = open("tissues.html","w","utf8")
	fid.write(Template(html_template).substitute(data))
	fid.close()
else:
	print r
