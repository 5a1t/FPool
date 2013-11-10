from twisted.web import server, resource
from twisted.internet import reactor
from struct import pack
import json
import array

def craft_response(gw_response):
	result = {}
	result['data'] = gw_response.gw_data
	result['target'] = gw_response.gw_target
	result['error'] = gw_response.gw_error
	result['id'] = gw_response.gw_id
	result = {'result': result}
	
	return json.dumps(result, ensure_ascii=False)


# Data section protocol via getwork specification.
# 80 bytes, 4 byte numbers = 20 numbers.
# Number 0 	: version (1 number)
# Number 1-8	: prevhash (8 numbers)
# Number 9-16	: merkroot (8 numbers)
# Number 17	: time ( 1 number)
# Number 18 	: difficulty (1 number)
# Number 19	: nonce (1 number)
# Pad result out to 960 bits (1024 (desired total section length)
#                             -64 bits for truncation info), 
# Set final 64 bits to body length above.
# For bitcoin, this is 0x0000000000000280 (80 bytes)
# Body length, prevhash, and merkroot are switched to little endian.
# aka byte blocks in their body are in reversed order.
#
# Supply version as integer, prevhash as hex, merkroot as hex
# time as int, difficulty as int, nonce as int.
def craft_data(version,prevhash,merkroot,time,difficulty,nonce):

	#convert fields to binary and pad them if necessary
	bin_version =  "{0:b}".format(version).zfill(32)
	bin_prevhash =  bin(int(prevhash, 16))[2:].zfill(256)
	bin_prevhash =  map(''.join, zip(*[iter(bin_prevhash)]*8))
	bin_prevhash.reverse()
	bin_prevhash = ''.join(bin_prevhash)
	bin_merkroot =  bin(int(merkroot, 16))[2:].zfill(256)
	bin_merkroot =  map(''.join, zip(*[iter(bin_merkroot)]*8))
	bin_merkroot.reverse()
	bin_merkroot = ''.join(bin_merkroot)
	bin_time =  "{0:b}".format(time).zfill(32)
	bin_difficulty =  "{0:b}".format(difficulty).zfill(32)
	bin_nonce=  "{0:b}".format(nonce).zfill(32)

	main_field = bin_version + bin_prevhash + bin_merkroot
	main_field = main_field + bin_time + bin_difficulty + bin_nonce

	#calculate length of main body and pad body to 960.
	length = len(main_field)
	main_field = main_field.ljust(960, "0")
	bin_length =  "{0:b}".format(length).zfill(64)
	bin_length =  map(''.join, zip(*[iter(bin_length)]*8))
        bin_length.reverse()
	bin_length = ''.join(bin_length)

	main_field = main_field + bin_length
	main_field = ('{:0{width}x}'.format(int(main_field,2), width=4)).rjust(256,"0")
	

	return main_field



class getwork_response():
	gw_data = "00000002b15704f4ecae05d077e54f6ec36da7f20189ef73b77603225ae56d2b00000000bcf59695a4e35a2f7535e1a86b306a3b08c212bf0b833764018fe39f01919381510c28111c0e8a3700000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000";
	gw_target= "00000000FFFF0000000000000000000000000000000000000000000000000000"
	gw_error = "null"
	gw_id = 0

	#depreciated in bitcoin protocol, but may be required for compatibility.
	gw_midstate = ""
	gw_hash1 = ""


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
	self.gw_response.gw_data = craft_data(1,"0000000000000000000000000000000000000000000000000000000000000000","4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",1231006505,486604799,2083236893)

	return craft_response(self.gw_response) 


pool = server.Site(Pool())
reactor.listenTCP(8080, pool)
reactor.run()
