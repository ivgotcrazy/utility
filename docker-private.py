#!/usr/bin/python

import sys, httplib, json

def PrintHelp():
	print('''#######################################################################
[Desc]:
  This script is used to get all repositories from private registry.
[Usage]: 
  docker-pr registry-ip:registry-port
[Note]:
  192.168.5.177:5000 will be used if supply no argument.
#######################################################################''')

def IsValidArgv(argv):
	if len(argv) == 0:
		argv.append("192.168.5.177:5000")
		return True

	if len(argv) != 1:
		return False

	if len(argv[0].split(":")) != 2:
		return False

	return True
	
def Main(argv):
	if not IsValidArgv(argv):
		PrintHelp()
		sys.exit()

	[ip, port] = argv[0].split(":")
	try:
		http_client = httplib.HTTPConnection(ip, int(port), timeout=5)
		http_client.request('GET', '/v2/_catalog')
		catalog_resp = http_client.getresponse()
	except Exception, e:
		print e
		sys.exit()

	s = json.loads(catalog_resp.read())

	for repo in s["repositories"]:
		http_client.request('GET', '/v2/' + repo + '/tags/list')
		repo_json = json.loads(http_client.getresponse().read())
		for tag in repo_json["tags"]:
			print("%s:%s" % (repo_json["name"], tag))

if __name__ == "__main__":
	Main(sys.argv[1:])
