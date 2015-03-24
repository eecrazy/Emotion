import json
import urllib2
from emolist_new import emolist

#data = {"emo_type":2,"emo_id":2,"tags":["great","fantastic"]}

for data in emolist:

	req = urllib2.Request("http://182.92.110.241/anotate_emo/")
	req.add_header('Content-Type', 'application/json')

	response = urllib2.urlopen(req, json.dumps(data))
	resp =  response.read()
	resp_json = json.loads(resp)

	if int(resp_json.get("status",200)) == 400:
		print data
	else:
		print resp