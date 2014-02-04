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

from xml.dom.minidom import parse

import fxplib as Fxp


class Model:
    def __init__(self):
        pass

    # TODO : remove the parameters "screen_size" and "scale"
    #        then create the gui in another method (in view)
    def load_package(self, package, screen_size, scale=""):
        w, h = screen_size

        # create the input devices
        inputdev = Fxp.Input("inputdev")

        # create the gui layer
        gui = Fxp.Image("gui")
        gui.set_size(screen_size)
        gui.init_surface(screen_size)

        # create mouse cursor
        cursor = Fxp.Image("cursor", "packages/cursor.png")

        # create the root container
        builder = Fxp.Builder("packages/" + package)
        root = builder.root
        root.load_from_solid_color(Fxp.PALETTE.get_rgb("White", "light"),
                                   (w, h))
        root.scale = scale

        # define priorities
        gui.z = 1
        cursor.z = 10

        # pack objects
        gui.add_child(cursor)

        root.add_child(inputdev)
        root.add_child(gui)

        # send the root container
        return root

    def get_palette(self, filename):
        # parse xml file
        doc = parse(filename)

        # get name and create palette
        name = doc.childNodes[0].attributes["name"].value
        palette = Fxp.Palette(name)

        # get colorkey
        node = doc.getElementsByTagName("colorkey")[0]
        string = node.firstChild.nodeValue
        colorkey = self.split_color(string)
        palette.set_colorkey(colorkey)

        # get default color
        node = doc.getElementsByTagName("default")[0]
        string = node.firstChild.nodeValue
        palette.set_default(string)

        # get colors
        colors = doc.getElementsByTagName("color")
        for node in colors:
            # get color name
            colorname = node.attributes["name"].value
            color = Fxp.Color(colorname)

            # get values
            for child in node.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    if child.tagName == "value":
                        # get tone
                        tone = child.attributes["tone"].value

                        # get value
                        string = child.firstChild.nodeValue
                        value = self.split_color(string)

                        # add value
                        color.set_rgb(tone, value)

            # add color
            palette.append(color)

        doc.unlink()  # destroy dom object

        return palette

    def split_color(self, string):
        r, g, b = string.split(",", 3)
        return (int(r), int(g), int(b))

    def read_file(self, filename, mode, sizemax):
        f = open(filename, mode)

        # get size
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)

        # read
        if size <= sizemax:
            text = f.read()

        # close
        f.close()

        return text

    def get_license(self):
        return self.read_file("COPYING", "r", 1048576)  # 1 Mio max

    def get_authors(self):
        text = self.read_file("AUTHORS", "r", 1048576)  # 1 Mio max
        return text.split('\n')
