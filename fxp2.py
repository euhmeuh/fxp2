#!/usr/bin/env python2
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

from view import View
from model import Model
from controller import Controller

# profiler
#import cProfile


class Main:
    def __init__(self):
        # Model-View-Controller creation
        self.model = Model()
        self.view = View(self.model, (512, 384),
                         scale_mode="simple",
                         fullscreen=False)
        self.controller = Controller(self.model, self.view)

        # Start from the main menu
        self.controller.load_title()

    def start(self):
        self.controller.loop()

if __name__ == "__main__":
    main = Main()
    main.start()
