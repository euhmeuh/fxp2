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

import socket

class Main:
    def __init__(self):
        # configuration
        self.host = "localhost"
        self.port = 8448
        self.server = (self.host,self.port)
        
        self.commands = []
        #                     name    pattern  arguments
        self.commands.append(("list", "LIST",  0))
        self.commands.append(("owner","OWNER", 0))
        self.commands.append(("desc", "DESC",  0))
        self.commands.append(("motd", "MOTD",  0))
        #self.commands.append(("cmd", "CMD {} {}",  2))
        
        # open socket on UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def parse_command(self, command):
        cmd = command.split()
        for c in self.commands:
            if (cmd[0] == c[0] # if the commands matches
            and len(cmd)-1 == c[2]): # and the number of argument is correct
                return c[1].format(*cmd[1:]) # format the request

    def send(self, text):
        self.socket.sendto(text, self.server)

    def receive(self):
        return self.socket.recv(1024)

    def start(self):
        try:
            self.loop()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        print("\nGood bye!")
    
    def loop(self):
        message = ""
        while 1:
            # get command
            command = raw_input("Enter your message > ")
            if command in ("q","quit"):
                break
            
            if command in ("h","help"):
                print("Possible commands are: "
                     +"help, quit, "
                     +", ".join([c[0] for c in self.commands]))
                continue
            
            # parse it
            message = self.parse_command(command)
            if not message:
                print("Syntax error.")
                continue
            
            # send it
            self.send(message + "\n")
            
            # print response
            print(self.receive())
        
        self.stop()

if __name__ == "__main__":
    main = Main()
    main.start()

