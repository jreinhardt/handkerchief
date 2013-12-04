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
import subprocess
import re
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
			//this states which entries to filter, i.e. remove
			display_filter = {state: 'open'};
			function populate_menu(){
				//clear menu
				filtered_items = document.getElementById("filtered");
				while (filtered_items.hasChildNodes()) {
					filtered_items.removeChild(filtered_items.lastChild);
				}

				for(var i = 0; i < issue_data.length; i++){
					if(issue_data[i]['state'] != display_filter.state){
						var issue_title = document.createTextNode(issue_data[i]["title"])

						var issue_link = document.createElement("a");
						issue_link.setAttribute("href",'javascript:reload_content(' + issue_data[i]["number"].toString() + ')')
						issue_link.appendChild(issue_title);

						var issue_item = document.createElement("li")
						issue_item.appendChild(issue_link)

						filtered_items.appendChild(issue_item);
					}
				}
			}
			function toggle_state_filter(){
				if (display_filter.state == 'open'){
					display_filter.state = 'closed';
					document.getElementById("state_filter").innerHTML = 'State: Open';
				} else if (display_filter.state == 'closed'){
					display_filter.state = 'both';
					document.getElementById("state_filter").innerHTML = 'State: Both';
				} else if (display_filter.state == 'both'){
					display_filter.state = 'open';
					document.getElementById("state_filter").innerHTML = 'State: Closed';
				}
				populate_menu();
			}

		</script>
		<style>
			div#wrapper { width: 100%, min-width:800; position:relative;}
			div#menu { width:40%; position:absolute; left:0; font-size:small;}
			div#col_right { width:60%; position:absolute; right:0;}
			div.comment {margin: 10px; width: 80%; padding: 10px; border: 1px solid grey;}
		</style>
	</head>
	<body onload="populate_menu()">
		<div id="wrapper">
			<div id = "menu">
				<ul>
					<li><a id="state_filter" href="javascript:toggle_state_filter()">State: Closed</a></li>
				<ul id = "filtered">
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

#url must contain some parameters
def get_all_pages(url):
	url_temp = url + "&page=%d"

	data = []
	i = 1
	request = requests.get(url_temp % i)
	data += request.json()
	re_last_page = '<https://api.github.com/repositories/([0-9]*)/issues/comments\?page=([0-9]*)>; rel="last"'
	last_page = int(re.match(re_last_page,request.headers["link"].split(',')[-1].strip()).group(2))
	
	for i in range(2,last_page+1):
		request = requests.get(url_temp % i)
		data += request.json()
	return data

#try to figure out repo from git repo in current directory
reponame = None
try:
	remote_data = subprocess.check_output(["git","remote","-v","show"])
	branches = {}
	for line in remote_data.split("\n"):
		if line.strip() == "":
			continue
		remote_match = re.match("([a-zA-Z0-9_]*)\s*git@github.com:([a-zA-Z0-9_/]*)\.git\s*\(([a-z]*)\)",line)
		if not remote_match is None:
			branches[remote_match.group(1)] = remote_match.group(2)

	reponame = branches.values()[0]
	if "origin" in branches:
		reponame = branches["origin"]
except OSError:
	pass

parser = argparse.ArgumentParser("Download GitHub Issues into self-contained HTML file")
parser.add_argument("-o",dest="outname",default="issues.html",help="filename of output HTML file")
parser.add_argument("reponame",default=reponame,nargs="?",help="Name of the repo in the form username/reponame. If not given, handkerchief tries to figure it out from git.")

args = parser.parse_args()

issues = []
try:
	for state in ["open","closed"]:
		issue_request = requests.get('https://api.github.com/repos/%s/issues?state=%s&filter=all&direction=asc' % (args.reponame,state))
		if issue_request.ok:
			issues += issue_request.json()
		else:
			print "There is a problem with the request"
			print issue_request
			exit(1)
	comments = get_all_pages('https://api.github.com/repos/%s/issues/comments?' % args.reponame)
except requests.exceptions.ConnectionError:
	print "Could not connect to GitHub. Please check your internet connection"
	exit(1)

#menulinks = []
#for issue in data["issue_data"]:
#	nr = int(issue["number"])
#	menulinks.append("""<li><a href="javascript:reload_content('%d')">#%d: %s</a></li>""" % (nr,nr,issue["title"]))
#data["menulinks"] = "\n".join(menulinks)

data = {}
data["issue_data"] = json.dumps(issues)
data["comment_data"] = json.dumps(comments)

fid = open(args.outname,"w","utf8")
fid.write(Template(html_template).substitute(data))
fid.close()
