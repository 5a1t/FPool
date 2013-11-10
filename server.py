from twisted.web import server, resource
from twisted.internet import reactor

class Pool(resource.Resource):
    def render_GET(self, request):
	print "get"
	request.setHeader("Content-Type", "text/plain; charset=utf-8")
        return "<html><h1>Welcome to fpool!</h1></html>"

pool = server.Site(Pool())
reactor.listenTCP(8080, pool)
reactor.run()
