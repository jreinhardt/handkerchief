#!/usr/bin/env python
# Handkerchief: A GitHub Issues offline reader
# https://github.com/jreinhardt/handkerchief
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>
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
import base64
from sys import exit
from string import Template
from codecs import open
from jinja2 import Environment, FileSystemLoader, BaseLoader
from os.path import join

re_mote = re.compile("([a-zA-Z0-9_]*)\s*((git@github.com\:)|(https://github.com/))([a-zA-Z0-9_/]*)\.git\s*\(([a-z]*)\)")

issue_url = 'https://api.github.com/repos/%s/issues?state=%s&filter=all&direction=asc'
issue_last_re = '<https://api.github.com/repositories/([0-9]*)/issues\?state=%s&filter=all&direction=asc&page=([0-9]*)>; rel="last"'

comment_url = 'https://api.github.com/repos/%s/issues/comments?'
comment_last_re = '<https://api.github.com/repositories/([0-9]*)/issues/comments\?page=([0-9]*)>; rel="last"'

label_url = 'https://api.github.com/repos/%s/labels?'
label_last_re = '<https://api.github.com/repositories/([0-9]*)/labels\?page=([0-9]*)>; rel="last"'

milestone_url = 'https://api.github.com/repos/%s/milestones?'
milestone_last_re = '<https://api.github.com/repositories/([0-9]*)/milestones\?page=([0-9]*)>; rel="last"'

repo_url = 'https://api.github.com/repos/%s?'
file_url = 'https://api.github.com/repos/%s/contents/%s'

avatar_style = "div.%s {background-image: url(data:image/png;base64,%s); background-size: 100%% 100%%;}\n"

def get_github_content(repo,path):
	request = requests.get(file_url % (repo,path))
	if not request.ok:
		print "There is a problem with the request"
		print file_url % (repo,path)
		print request
		exit(1)
	if not request.json()['encoding'] == 'base64':
		raise RuntimeError("Unknown Encoding encountered when fetching %s from repo %s: %s" % (path,repo,request.json()['encoding']))
	return request.json()['content'].decode('base64').decode('utf8')

class GitHubLoader(BaseLoader):
	def __init__(self, repo, layout):
		self.repo = repo
		self.layout = layout

	def get_source(self, environment, template):
		source = get_github_content(self.repo,'templates/%s/%s' % (self.layout,template))
		return source,None, lambda: False

#url must contain some parameters
def get_all_pages(url,re_last_page):
	url_temp = url + "&page=%d"

	data = []
	i = 1
	request = requests.get(url_temp % i)
	if not request.ok:
		print "There is a problem with the request"
		print url_temp % i
		print request
		exit(1)
	data += request.json()
	if not 'link' in request.headers:
		#only one page
		return data
	else:
		result = re.match(re_last_page,request.headers["link"].split(',')[-1].strip())
		if result is None:
			print request.headers["link"]

		last_page = int(result.group(2))
		
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
		remote_match = re_mote.match(line)
		if not remote_match is None:
			branches[remote_match.group(1)] = remote_match.group(5)

	reponame = branches.values()[0]
	if "origin" in branches:
		reponame = branches["origin"]
except OSError:
	pass

#parse command line arguments
parser = argparse.ArgumentParser("Download GitHub Issues into self-contained HTML file")
parser.add_argument("-o",dest="outname",default="issues.html",help="filename of output HTML file")
parser.add_argument("-t",dest="template",default="default",help="filename of a template to use")
parser.add_argument("-l",dest="local",action="store_true",help="use local templates instead")
parser.add_argument("-a",dest="local_avatars",action="store_false",help="do not embed avatars, leads to smaller results")
parser.add_argument("reponame",default=reponame,nargs="?",help="Name of the repo in the form username/reponame. If not given, handkerchief tries to figure it out from git.")

args = parser.parse_args()

#request data from api
data = {}
try:
	data['issues']= []
	for state in ["open","closed"]:
		data['issues']+= get_all_pages(issue_url % (args.reponame,state),issue_last_re % state)

	repo_request = requests.get(repo_url % args.reponame)
	if not repo_request.ok:
		print "There is a problem with the request"
		print repo_url % args.reponame
		print repo_request
		exit(1)
	data['repo'] = repo_request.json()
	
	data['comments'] = get_all_pages(comment_url % args.reponame, comment_last_re)
	data['labels'] = get_all_pages(label_url % args.reponame, label_last_re)
	data['milestones'] = get_all_pages(milestone_url % args.reponame, milestone_last_re)

except requests.exceptions.ConnectionError:
	print "Could not connect to GitHub. Please check your internet connection"
	exit(1)

data['javascript'] = []
data['stylesheets'] = []

#fetch avatars and convert to base64
if args.local_avatars:
	av_style = ""
	avatars = []
	for comment in data['comments']:
		url = comment['user']['avatar_url']
		avclass = 'avatar_' + comment['user']['login']
		if not avclass in avatars:
			r = requests.get(url)
			if r.status_code == 200:
				av_style += avatar_style % (avclass,base64.b64encode(r.content))
				avatars.append(avclass)
		comment['user']['avatar_class'] = avclass
	data['stylesheets'].append(av_style)

#process parameters
if args.local:
	troot = join("templates",args.template)
	params = json.load(open(join(troot,"%s.json" % args.template)))

	#load template
	env = Environment(loader=FileSystemLoader(troot))
	template = env.get_template(params['html'])

	data['javascript'] = [{'name' : n, 'content' : open(join(troot,n)).read()} for n in params['js']]
	data['stylesheets'] = [open(join(troot,n)).read() for n in params['css']]
else:
	params = get_github_content('jreinhardt/handkerchief','templates/%s/%s.json' % (args.template,args.template))
	params = json.loads(params)

	#load template
	env = Environment(loader=GitHubLoader('jreinhardt/handkerchief',args.template))
	template = env.get_template(params['html'])

	for n in params['js']:
		content = get_github_content('jreinhardt/handkerchief','templates/%s/%s' %(args.template,n))
		data['javascript'].append({'name' : n, 'content' : content})
	for n in params['css']:
		content = get_github_content('jreinhardt/handkerchief','templates/%s/%s' %(args.template,n))
		data['stylesheets'].append(content)

#populate template
fid = open(args.outname,"w","utf8")
fid.write(template.render(data))
fid.close()
