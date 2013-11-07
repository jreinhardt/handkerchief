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
