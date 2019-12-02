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


base_url = "http://localhost:5280/files"


def fill_queue(the_queue):
    the_queue.put_nowait({"time": 1475931040,
                          "message": '{"subject": "SIMULATION","status": "started"}'})
    the_queue.put_nowait({"time": 1475931047,
                          "message": '{"subject": "CREATE_PRODUCER", "type": "PV", "id": "[0]:[1]", '
                                     '"profile":"' + base_url + '/producer.csv"}'})
    the_queue.put_nowait({"time": 1475932000,
                          "message": '{"subject": "LOAD", "id": "[0]:[1]:[1]", "sequence": 1, "est": 1475932000, '
                                     '"lst": 1475939000,  "profile": "' + base_url + '/0_run_1.csv"}'})
    the_queue.put_nowait({"time": 1475935000,
                          "message": '{"subject": "ATTACH_HC_DEVICE", "id": "[0]:[2]:[1]", '
                                     '"profile": "' + base_url + '/0_2_1.csv"}'})
    the_queue.put_nowait({"time": 1475991040,
                          "message": '{"subject": "SIMULATION","status": "stopped"}'})


class WebAgent(agent.Agent):
    
    dispatched = queue.Queue()
    simulated_time = -1

    def setup(self):
        fill_queue(self.dispatched)
        self.web.start(templates_path="examples")
        self.traces.reset()

    async def get_message(self, request):
        if self.dispatched.empty():
            fill_queue(self.dispatched)
        nextmsg = self.dispatched.get_nowait()
        self.simulated_time = nextmsg["time"]
        return {"time": nextmsg["time"], "message": nextmsg["message"]}

    async def get_time(self, request):

        return {"time": self.simulated_time, "message": '{"subject": "TIME", "time": ' + str(self.simulated_time) + '}'}

    async def my_post_controller(self, request):
        form = await request.post()
        print(form)

@click.command()
@click.option('--jid', prompt="Agent JID> ")
@click.option('--pwd', prompt="Password>", hide_input=True)
@click.option('--port', default=10001)
def run(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port

    a.web.add_get("/getmessage", a.get_message, "message.html")
    a.web.add_get("/gettime", a.get_time, "message.html")
    a.web.add_post("/postmessage",a.my_post_controller, None)

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
