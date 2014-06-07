import base64
import requests
r = requests.get("https://avatars.githubusercontent.com/u/1331555?")
if r.status_code == 200:
	res = base64.b64encode(r.content)

with open("test.html","w") as fid:
	fid.write("""
<!DOCTYPE html>
<html>
	<head>
	</head>
	<body><img src="data:image/png;base64,%s" alt="jreinhardt" />
	</body>
</html>
""" % res)

