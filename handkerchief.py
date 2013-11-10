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

import argparse
import requests
import json
from sys import exit
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
				var comment_node = document.getElementById("comments");
				while (comment_node.hasChildNodes()) {
					comment_node.removeChild(comment_node.lastChild);
				}

				for(var i = 0; i < issue_data.length; i++){
					if(issue_data[i]["number"] == id){
						document.getElementById("title").firstChild.nodeValue = issue_data[i]["title"];

						var comment = document.createElement("div");
						comment.setAttribute("class","comment");
						comment.appendChild(document.createTextNode(issue_data[i]["body"]));
						comment_node.appendChild(comment);
						for(var j = 0; j < comment_data.length; j++){
							if(comment_data[j]["issue_url"] == issue_data[i]["url"]){
								var comment = document.createElement("div");
								comment.setAttribute("class","comment");
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
			.comment {margin: 10px; width: 80%;}
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
				<h3 id = "title">
				</h3>
				<div id = "comments">
				</div>
			</div>
		</div>
	</body>
</html>
"""

parser = argparse.ArgumentParser("Download GitHub Issues into self-contained HTML file")
parser.add_argument("-o",dest="outname",default="issues.html",help="filename of output HTML file")
parser.add_argument("reponame",help="name of the repo in the form username/reponame")

args = parser.parse_args()

try:
	issue_request = requests.get('https://api.github.com/repos/%s/issues?state=open&filter=all&direction=asc' % args.reponame)
	comment_request = requests.get('https://api.github.com/repos/%s/issues/comments' % args.reponame)
except requests.exceptions.ConnectionError:
	print "Could not connect to GitHub. Please check your internet connection"
	exit(1)

if issue_request.ok and comment_request.ok:
	data = {}
	data["issue_data"] = issue_request.text or issue_request.content
	data["comment_data"] = comment_request.text or comment_request.content

	menulinks = []
	for issue in json.loads(data["issue_data"]):
		nr = int(issue["number"])
		menulinks.append("""<li><a href="javascript:reload_content('%d')">#%d: %s</a></li>""" % (nr,nr,issue["title"]))
	data["menulinks"] = "\n".join(menulinks)

	fid = open(args.outname,"w","utf8")
	fid.write(Template(html_template).substitute(data))
	fid.close()
else:
	print "There was a problem with the API request:"
	print r
	exit(1)
