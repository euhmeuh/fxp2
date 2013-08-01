#!/usr/bin/python2
# -*- coding: utf8 -*-

# fxp2 - Multiplayer platform RPG
# Copyright (C) 2009 - 2013 MARTIN Jérôme <poupoule.studios@sfr.fr>
# This file is part of the fxp2 program.
# 
# fxp2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# fxp2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import SocketServer 

class ServerData:
    def __init__(self):
        self.serverlist = []
        self.description = ""
        self.owner = ""
        self.motd = ""

class Client(SocketServer.BaseRequestHandler):
    def handle(self):
        # get client request
        request = self.request[0].strip()
        socket = self.request[1]
        
        # print it for debug
        self.server.log("Request from <"+self.client_address[0]+"> : "+request)
        
        # process request
        r = request.split()
        response = ""
        if r[0] == "LIST":
            for srv in self.server.data.serverlist:
                response += "SRV \""+srv[0]+"\" \""+srv[1]+"\" "+str(srv[2])+" "+str(srv[3])+"\n"
        elif r[0] == "DESC":
            response = "DESC \""+self.server.data.description+"\""
        elif r[0] == "OWNER":
            response = "OWNER \""+self.server.data.owner+"\""
        elif r[0] == "MOTD":
            response = "MOTD \""+self.server.data.motd+"\""
        
        # send a response to the client
        if response:
            socket.sendto(response, self.client_address)

class MasterServer:
    def __init__(self):
        self.bound = "0.0.0.0"
        self.port = 8448
        self.data = ServerData()
        
        # set server data
        self.data.description = "FXP2 Master Server #1"
        self.data.owner = "EuhMeuh"
        self.data.motd = "[2013-04-13] The server may be a bit derpy, but it works!"
        self.data.serverlist.append(("46.51.197.89","Rilouworld",2,20))
        self.data.serverlist.append(("173.194.67.121","Equestria",12,40))
        self.data.serverlist.append(("108.162.203.19","Mitakihara",12,40))

    def welcome(self):
        self.log("Final Experience 2 Master Server 0.1")
        self.log("Server informations :")
        self.log("Description: \""+ self.data.description +"\"")
        self.log("Owner:       \""+ self.data.owner + "\"")
        self.log("MOTD:        \""+ self.data.motd + "\"")

    def bind(self):
        self.log("Binding adress "+ self.bound +" on port "+ str(self.port))
        
        # bind address on UDP
        self.instance = SocketServer.UDPServer((self.bound, self.port), Client)
        self.instance.data = self.data
        self.instance.log = self.log

    def fetch(self):
        self.log("Fetching servers...")
        for srv in self.data.serverlist:
            self.log("Server found: "+ srv[0] +" \""+ srv[1] + "\" ("+ str(srv[2]) +"/"+ str(srv[3]) +")")

    def start(self):
        self.welcome()
        self.bind()
        self.fetch()
        self.loop()

    def stop(self):
        print("\n:: Received interruption signal. Stopping server.")

    def loop(self):
        self.log("Waiting for clients...")
        try:
            self.instance.serve_forever()
        except KeyboardInterrupt:
            self.stop()

    def log(self, message):
        print(":: "+message)

if __name__ == "__main__":
    server = MasterServer()
    server.start()

