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


class WebAgent(agent.Agent):
    
    message_queue=[]
    
    
    def setup(self):
        self.web.start(templates_path="examples")
        
        self.traces.reset()
     

   


@click.command()
@click.option('--jid', prompt="Agent JID> ")
@click.option('--pwd', prompt="Password>", hide_input=True)
@click.option('--port', default=10000)
def run(jid, pwd, port):
    a = WebAgent(jid, pwd)
    a.web.port = port

    async def hello(request):
        return {"time":1568115549,"message": '{"subject": "CREATE_PRODUCER PV","id": "[0]:[1]", "profile": "http://host:port/simulation/profile.csv"}'}

    a.web.add_get("/getmessage", hello, "message.html")
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
