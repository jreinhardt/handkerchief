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
import getpass
import glob
import os
from sys import exit
from string import Template
from codecs import open
from jinja2 import Environment, FileSystemLoader, BaseLoader
from os.path import join, realpath, dirname

re_mote = re.compile("([a-zA-Z0-9_]*)\s*((git@github.com\:)|(https://github.com/))([a-zA-Z0-9_/]*)\.git\s*\(([a-z]*)\)")

issue_url = 'https://api.github.com/repos/%s/issues?state=%s&filter=all&direction=asc'
issue_last_re = '<https://api.github.com/repositories/([0-9]*)/issues\?state=%s&filter=all&direction=asc&page=([0-9]*)>; rel="last"'

comment_url = 'https://api.github.com/repos/%s/issues/comments?'
comment_last_re = '<https://api.github.com/repositories/([0-9]*)/issues/comments\?page=([0-9]*)>; rel="last"'
comment_issue_re = 'https://github.com/%s/issues/([0-9]*)#issuecomment-[0-9]*'

label_url = 'https://api.github.com/repos/%s/labels?'
label_last_re = '<https://api.github.com/repositories/([0-9]*)/labels\?page=([0-9]*)>; rel="last"'

milestone_url = 'https://api.github.com/repos/%s/milestones?'
milestone_last_re = '<https://api.github.com/repositories/([0-9]*)/milestones\?page=([0-9]*)>; rel="last"'

assignee_url = 'https://api.github.com/repos/%s/assignees?'
assignee_last_re = '<https://api.github.com/repositories/([0-9]*)/assignees\?page=([0-9]*)>; rel="last"'

repo_url = 'https://api.github.com/repos/%s?'
file_url = 'https://api.github.com/repos/%s/contents/%s'

avatar_style = "div.%s {background-image: url(data:image/png;base64,%s); background-size: 100%% 100%%;}\n"

repo_marker_re = "<!--\s*([^\s]*)\s-->"

def get_github_content(repo,path,auth=None):
	request = requests.get(file_url % (repo,path),auth=auth)
	if not request.ok:
		print "There is a problem with the request"
		print file_url % (repo,path)
		print request
		exit(1)
	if not request.json()['encoding'] == 'base64':
		raise RuntimeError("Unknown Encoding encountered when fetching %s from repo %s: %s" % (path,repo,request.json()['encoding']))
	return request.json()['content'].decode('base64').decode('utf8')

class GitHubLoader(BaseLoader):
	def __init__(self, repo, layout,auth=None):
		self.repo = repo
		self.layout = layout
		self.auth = auth

	def get_source(self, environment, template):
		source = get_github_content(self.repo,'layouts/%s/%s' % (self.layout,template),self.auth)
		return source,None, lambda: False

#url must contain some parameters
def get_all_pages(url,re_last_page,auth=None):
	url_temp = url + "&page=%d"

	data = []
	i = 1
	request = requests.get(url_temp % i,auth=auth)
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
			request = requests.get(url_temp % i,auth=auth)
			data += request.json()
		return data

def get_data(reponame,auth,local_avatars,states):
	data = {}
	data['reponame'] = reponame
	try:
		data['issues'] = []

		for state in states:
			data['issues']+= get_all_pages(issue_url % (reponame,state),issue_last_re % state,auth)

		repo_request = requests.get(repo_url % reponame,auth=auth)
		if not repo_request.ok:
			print "There is a problem with the request"
			print repo_url % reponame
			print repo_request
			exit(1)
		data['repo'] = repo_request.json()

		comments = get_all_pages(comment_url % reponame, comment_last_re,auth)
		data['labels'] = get_all_pages(label_url % reponame, label_last_re,auth)
		data['milestones'] = get_all_pages(milestone_url % reponame, milestone_last_re,auth)
		data['assignees'] = get_all_pages(assignee_url % reponame, assignee_last_re,auth)

	except requests.exceptions.ConnectionError:
		print "Could not connect to GitHub. Please check your internet connection"
		exit(1)

	data['javascript'] = []
	data['stylesheets'] = []

	#fetch avatars and convert to base64
	if local_avatars:
		av_style = ""
		avatars = []
		for item  in comments + data['issues']:
			url = item['user']['avatar_url']
			avclass = 'avatar_' + item['user']['login']
			if not avclass in avatars:
				r = requests.get(url,auth=auth)
				if r.status_code == 200:
					av_style += avatar_style % (avclass,base64.b64encode(r.content))
					avatars.append(avclass)
			item['user']['avatar_class'] = avclass
		data['stylesheets'].append(av_style)

	#determine issue ids for comments
	for issue in data['issues']:
		issue['comments_list'] = []
	for comment in comments:
		match = re.match(comment_issue_re % reponame,comment['html_url'])

		if not match is None:
			for issue in data['issues']:
				if int(issue['number']) == int(match.group(1)):
					issue['comments_list'].append(comment)
					break

	#add labelnames to issues
	for issue in data['issues']:
		issue['labelnames'] = [l['name'] for l in issue['labels']]
	return data

def main():
	reponames = []

	#try to figure out the repo from git repo in current directory
	try:
		with open(os.devnull) as devnull:
			remote_data = subprocess.check_output(["git","remote","-v","show"],stderr=devnull)
		branches = {}
		for line in remote_data.split("\n"):
			if line.strip() == "":
				continue
			remote_match = re_mote.match(line)
			if not remote_match is None:
				branches[remote_match.group(1)] = remote_match.group(5)
		if len(branches) > 0:
			if "origin" in branches:
				reponames.append(branches["origin"])
			else:
				reponames.append(branches.values()[0])
	except OSError:
		pass
	except subprocess.CalledProcessError:
		pass

	#scan html files for further repos to consider
	for fname in glob.iglob("*.html"):
		fid = open(fname,"r","utf8")
		#check the second line for the repo marker
		fid.readline()
		line = fid.readline()
		match = re.match(repo_marker_re,line)
		if not match is None:
			reponames.append(match.group(1))

		reponames = list(set(reponames))

	#parse command line arguments
	parser = argparse.ArgumentParser("Download GitHub Issues into self-contained HTML file")

	parser.add_argument("-o",dest="outname",default=None,
		help="filename of output HTML file")
	parser.add_argument("-l",dest="layout",default="default",
		help="name of a layout to use")
	parser.add_argument("-q",dest="verbose",default="store_false",
		help="suppress output to stdout")
	parser.add_argument("--state",dest="state",default="all",choices=["all","open","closed"],
		help="download issues of this state only")
	parser.add_argument("--local",dest="local",action="store_true",
		help="use local layouts instead, useful during development")
	parser.add_argument("-a",dest="auth",action="store_true",
		help="authenticate, is sometimes necessary to avoid rate limiting")
	parser.add_argument("--user", help="Username for authentication",
		default=os.environ.get("GITHUB_USERNAME"))
	parser.add_argument("--token", help="Use Github token for authentication instead of password",
		default=os.environ.get("GITHUB_ACCESS_TOKEN"))
	parser.add_argument("--no-local-avatars",dest="local_avatars",action="store_false",
		help="do not embed avatars, leads to smaller results")
	parser.add_argument("reponame",default=reponames,nargs="*",
		help="GitHub repo in the form username/reponame. If not given, handkerchief guesses")

	args = parser.parse_args()

	if len(args.reponame) == 0:
		print "No repository was given and handkerchief failed to guess one"
		exit(1)

	if len(args.reponame) > 1 and not args.outname is None:
		print "Output filename is impossible if multiple repos are given"
		exit(1)


	if args.token or args.auth:
		username = args.user or raw_input("Username: ")
		if args.token:
			auth = (username, args.token)
		else:
			auth = (username, getpass.getpass())
	else:
		auth = None

	#process parameters
	layout_js = []
	layout_css = []
	if args.local:
		root = dirname(realpath(__file__))
		lroot = join(root,"layouts",args.layout)
		params = json.load(open(join(lroot,"%s.json" % args.layout),"r","utf8"))

		#load layout
		env = Environment(loader=FileSystemLoader(lroot))
		template = env.get_template(params['html'])

		layout_js = [{'name' : n, 'content' : open(join(lroot,n),"r","utf8").read()} for n in params['js']]
		layout_css = [open(join(lroot,n),"r","utf8").read() for n in params['css']]
	else:
		params = get_github_content('jreinhardt/handkerchief','layouts/%s/%s.json' % (args.layout,args.layout),auth)
		params = json.loads(params)

		#load layout
		env = Environment(loader=GitHubLoader('jreinhardt/handkerchief',args.layout,auth))
		template = env.get_template(params['html'])

		for n in params['js']:
			content = get_github_content('jreinhardt/handkerchief','layouts/%s/%s' %(args.layout,n),auth)
			layout_js.append({'name' : n, 'content' : content})
		for n in params['css']:
			content = get_github_content('jreinhardt/handkerchief','layouts/%s/%s' %(args.layout,n),auth)
			layout_css.append(content)

	for repo in args.reponame:
		#request data from api
		if args.verbose:
			print "Fetching data for %s ..." % repo
		if args.state == "all":
			states = ["open","closed"]
		else:
			states = [args.state]
		data = get_data(repo,auth,args.local_avatars,states)
		data['javascript'] += layout_js
		data['stylesheets'] += layout_css

		#populate template
		outname = args.outname or "issues-%s.html" % repo.split("/")[1]
		with open(outname,"w","utf8") as fid:
			fid.write(template.render(data))

if __name__ == '__main__':
	main()
