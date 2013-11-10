from twisted.web import server, resource
from twisted.internet import reactor
import json

def craft_response(gw_response):
	result = {}
	result['data'] = gw_response.gw_data
	result['target'] = gw_response.gw_target
	result['error'] = gw_response.gw_error
	result['id'] = gw_response.gw_id
	result = {'result': result}
	
	return json.dumps(result, ensure_ascii=False)


class getwork_response():
	gw_data = "00000002b15704f4ecae05d077e54f6ec36da7f20189ef73b77603225ae56d2b00000000bcf59695a4e35a2f7535e1a86b306a3b08c212bf0b833764018fe39f01919381510c28111c0e8a3700000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000";
	gw_target= "00000000FFFF0000000000000000000000000000000000000000000000000000"
	gw_error = "null"
	gw_id = 0


class pool_config():
	longpoll = " ";


class Pool(resource.Resource):
    gw_response = getwork_response()

    isLeaf = True
    def render_GET(self, request):
	print "GET"
	print request.requestHeaders
	print request.content.read()
	request.setHeader("Content-Type", "text/plain; charset=utf-8")
        return "<html><h1>Welcome to fpool!</h1></html>"

    def render_POST(self, request):
	print "POST"
	print request.requestHeaders
	print request.content.read()
	return craft_response(self.gw_response) 

pool = server.Site(Pool())
reactor.listenTCP(8080, pool)
reactor.run()
