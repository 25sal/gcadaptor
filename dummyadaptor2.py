# coding=utf-8
import asyncio
import datetime
import random
import time

import aioxmpp
import click
from aioxmpp import PresenceType, Presence, JID, PresenceShow, MessageType
from aioxmpp.roster.xso import Item

from spade import agent, behaviour
from spade.behaviour import State
from spade.message import Message
from spade.template import Template
import json
import queue
from aiohttp import web as aioweb
import aiohttp_cors

base_url = "http://parsec2.unicampania.it:5280/files"


def fill_queue(the_queue):
    the_queue.put_nowait({"sim_id":"demo",
			   "time": 1475931040,
                          "message": {"subject": "SIMULATION","status": "started"}})
    the_queue.put_nowait({"sim_id":"demo",
			  "time": 1475931047,
                          "message": {"subject": "CREATE_PRODUCER", "type": "PV", "id": "[0]:[1]", 
                                     "profile":  str(base_url + '/demo/input/producer.csv')}})
    the_queue.put_nowait({"sim_id":"demo",
			  "time": 1475932000,
                          "message": {"subject": "LOAD", "id": "[0]:[1]:[1]", "sequence": 1, "est": 1475932000, 
                                     "lft": 1475948000,  "profile": str(base_url + '/demo/input/0_run_1.csv'), "demo": str(base_url+'/gcharge/index.html')}})
    the_queue.put_nowait({"sim_id":"demo",
			  "time": 1475935000,
                          "message": {"subject": "HC_LOAD", "id": "[0]:[2]:[1]", "sequence":1,
                                     "profile": str(base_url + '/demo/input/0_2_1.csv'),"demo": str(base_url+'/gcharge/indexhc.html')}})
    the_queue.put_nowait({"sim_id":"demo",
			  "time": 1475991040,
                          "message": {"subject": "SIMULATION","status": "stopped"}})


class WebAgent(agent.Agent):
    
    dispatched = queue.Queue()
    simulated_time = -1

    def setup(self):
        fill_queue(self.dispatched)
        self.web.start(hostname="parsec2.unicampania.it", templates_path="examples")
        self.traces.reset()

    async def get_message(self, request):
        if self.dispatched.empty():
            fill_queue(self.dispatched)
        nextmsg = self.dispatched.get_nowait()
        self.simulated_time = nextmsg["time"]
        res = {"sim_id": nextmsg["sim_id"], "time": nextmsg["time"], "message": nextmsg["message"]}
        return aioweb.json_response(res)
	#return {"sim_id": nextmsg["sim_id"], "time": nextmsg["time"], "message": nextmsg["message"]}

    async def get_time(self, request):

        return {"sim_id": '"demo"', "time": self.simulated_time, "message": '{"subject": "TIME", "time": ' + str(self.simulated_time) + '}'}

    async def my_post_controller(self, request):
        form = await request.post()
        print(form)

@click.command()
@click.option('--jid', prompt="Agent JID> ")
@click.option('--pwd', prompt="Password>", hide_input=True)
@click.option('--port', default=10002)
def run(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port
    a.web.hostname="parsec2.unicampania.it"
    #a.web.add_get("/getmessage", a.get_message, "message.html")
    a.web.add_get("/gettime", a.get_time, "message.html")
    a.web.add_post("/postmessage",a.my_post_controller, None)
    cors = aiohttp_cors.setup(a.web.app, defaults={
	"*": aiohttp_cors.ResourceOptions(
		allow_credentials=True,
		expose_headers = "*",
		allow_headers = "*",
		allow_methods = "*",
	)
    })
    route = {
	'method' : 'GET',
	'path': '/getmessage',
	'handler' : a.get_message,
	'name' : 'test'
    }

    cors.add(a.web.app.router.add_route(method=route['method'],path=route['path'],handler=route['handler'],name=route['name']))
   
    a.start(auto_register=True)

    print("Agent web at {}:{}".format(a.web.hostname, a.web.port))
    print(a.jid)
    while a.is_alive():
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            a.stop()


if __name__ == "__main__":
    run()
