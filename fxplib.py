#!/usr/bin/env python2
# -*- coding: utf8 -*-

# fxplib - Game creation library
# Copyright (C) 2009 - 2013 MARTIN Jérôme <poupoule.studios@sfr.fr>
# This file is part of the fxplib library.
# 
# fxplib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# fxplib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame
pygame.init()

import math, operator
import xml.etree.ElementTree as ET

# global palette and font are
# mandatory to use Fxplib FIXME
PALETTE = None
FONT = None

#-------------------------------------------------------------------------------
# CORE
#-------------------------------------------------------------------------------

class Object:
    def __init__(self, name):
        # general
        self.name = name
        self.objects = {}
        self.signals = {}

        self.z = 0.0

    def __repr__(self):
        string = "<Fxp."+self.__class__.__name__+" ("+str(self.name)+")>"

        # children (recursive)
        for child in self.objects.values():
            string += "\n\t"+str(child).replace("\t", "\t\t")

        return string

    def add_child(self, obj):
        if not obj.name in self.objects:
            self.objects[obj.name] = obj

    def get_sorted_children(self):
        # return children sorted by priority
        return sorted(self.objects.values(), key=operator.attrgetter("z"))

    def get_child(self, path):
        name, sep, rest = path.partition("/")
        
        try:
            if rest != "":
                return self.objects[name].get_child(rest)
            else:
                return self.objects[name]
        except KeyError:
            return None

    def add_signal(self, name):
        if not name in self.signals:
            self.signals[name] = Signal(name)
    
    def get_signal(self, name):
        if name in self.signals:
            return self.signals[name]

    def connect_signal(self, name, function, data=None):
        if name in self.signals:
            self.signals[name].add_function(function, data)

    def emit_signal(self, name, response=None):
        if name in self.signals:
            self.signals[name].activate(True, response)
    
    # NOTE : recursive
    def execute_signals(self):
        for obj in self.objects.values():
            obj.execute_signals()
        
        for signal in self.signals.values():
            signal.execute(self)

    # NOTE : recursive
    def tick(self, time):
        for obj in self.get_sorted_children():
            obj.tick(time)

    # NOTE : recursive
    def render(self, surface):
        for obj in self.get_sorted_children():
            obj.render(surface)

    # NOTE : recursive
    def check_force(self):
        for obj in self.objects.values():
            obj.check_force()

    # NOTE : recursive
    def update_focus(self, mouse_pos):
        for obj in self.objects.values():
            obj.update_focus(mouse_pos)

    # NOTE : recursive
    def update_state(self, mouse_but):
        for obj in self.objects.values():
            obj.update_state(mouse_but)

    # NOTE : recursive
    def move_all(self, vectors=True, move=True):
        for obj in self.objects.values():
            obj.move_all(vectors, move)

class Signal:
    def __init__(self, name):
        self.name = name
        self.functions = []
        self.responses = []
        self.activated = False
        
    def activate(self, boolean, response=None):
        self.activated = boolean
        if response:
            self.responses.append(response)

    def add_function(self, function, data=None):
        self.functions.append((function, data))

    def execute(self, obj):
        if(self.activated):
            def play(response=None):
                for func, data in self.functions:
                    func(obj, response, data)
            
            if self.responses:
                for response in self.responses:
                    play(response)
            else:
                play()
            
            self.activated = False
            self.responses = []

class Vector:
    def __init__(self, name=None, polar=(0,0)):
        self.x = 0
        self.y = 0
        self.name = name
        self.enable = True
        self.set_polar_pos(polar)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        
        if x > -0.0001 and x < 0.0001:
            x = 0
        
        if y > -0.0001 and y < 0.0001:
            y = 0
        
        new = Vector()
        new.set_pos((x, y))
        return new

    def __neg__(self):
        x = - self.x
        y = - self.y
        new = Vector()
        new.set_pos((x, y))
        return new

    def __mul__(self, other):
        x = self.x * other
        y = self.y * other
        new = Vector()
        new.set_pos((x, y))
        return new
    
    __rmul__ = __mul__
    
    def __repr__(self):
        return "<Fxp.Vector ("+str(self.x)+","+str(self.y)+")>"

    def get_pos(self):
        return (self.x, self.y)

    def set_pos(self, pos):
        x, y = pos
        self.x, self.y = x, y

    def get_polar_pos(self):
        r = math.sqrt(pow(self.x, 2) + pow(self.y, 2))
        a = math.atan2(self.y, self.x) / math.pi
        
        return (r, a)

    def set_polar_pos(self, polar):
        r, a = polar
        x = r * math.cos(a*math.pi)
        y = r * math.sin(a*math.pi)
        self.set_pos((x,y))

class Image (Object):
    def __init__(self, name, filename=None):
        Object.__init__(self, name)
        
        # positions and graphics
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.z = 0.0
        
        self.x_offset = 0
        self.y_offset = 0
        
        self.grid_size = 1

        self.h_mirrored = False
        self.v_mirrored = False

        self.h_mode = ""
        self.v_mode = ""
        
        self.state = "IDLE" # IDLE, MOUSEOVER, CLICKED
        self.surface = None
        self.image = None
        self.frames = {}
        self.frame = ""
        self.last_tick = 0
        
        self.focused = False
        self.display = True
        self.force = False
        self.scale = "" # Nothing, "simple" or "scale2x"
        
        self.filename = filename
        
        # open image if filename is given
        if filename:
            self.load_from_file(filename)
        
        # create signals
        self.add_signal("click")
        self.add_signal("mouseover")

    def load(self):
        pass

    def load_from_solid_color(self, color, size):
        self.image = Surface(size)
        self.image.fill(color)
        
        self.set_size(size)

    def load_from_file(self, filename):
        image = pygame.image.load(filename)
        w, h = image.get_size()

        temp = Surface((w,h))
        temp.blit(image, (0,0))

        self.image = temp
        
        self.set_size((w, h))

    def load_from_stock(self, stock_id):
        pass
    
    def init_surface(self, size):
        self.surface = Surface(size)

    def mirror(self, horizontal=True, rect=None):
        """ Load a mirrored copy of the image in memory
            that will be used when flip() is called.

            The object's image's size is doubled to make room for
            the mirrored version.

            So after calling this method, the object will have
            an image twice as big as before, with the first part being the
            normal version, and the second part being the mirrored one.

            Everything will be on the *same* surface!

            The optional "rect" argument must be used when the image
            is composed of multiple frames. It specifies the size of
            the frames, so that the mirror is applied to each, starting
            from the upper-left corner.
        """
        # if the image is not set, we quit
        if not self.image:
            return

        # if the axis has already been mirrored, we quit
        if horizontal and self.h_mode == "mirrored":
            return
        if not horizontal and self.v_mode == "mirrored":
            return
        
        # get the corresponding dimensions
        iw, ih = self.image.get_size()
        if horizontal:
            w = iw * 2
            h = ih
        else:
            w = iw
            h = ih * 2
        
        # create a new surface
        temp = Surface((w, h))
        
        # blit self image on the new surface
        temp.blit(self.image, (0,0))

        # check optional rect argument
        if rect:
            rw = rect[0]
            rh = rect[1]
            t = Surface((rw, rh))
        else:
            rw = iw
            rh = ih
            t = self.image

        # flip and blit image frame by frame
        for y in range(0, ih, rh):
            for x in range(0, iw, rw):
                # extract frame
                if t is not self.image:
                    t.clear()
                    t.blit(self.image, (0,0), area=(x,y,rw,rh))

                # blit flipped frame
                if horizontal:
                    img = pygame.transform.flip(t, True, False)
                    temp.blit(img, (iw+x, y))
                else:
                    img = pygame.transform.flip(t, False, True)
                    temp.blit(img, (x, ih+y))
        
        # apply the new surface
        self.image = temp
        self.surface = None
        
        if horizontal:
            self.h_mode = "mirrored"
        else:
            self.v_mode = "mirrored"

    def flip(self, horizontal=True, state=None):
        """ Define the direction of the object.
            If state is not passed, toggle the direction.

            The direction is used to know whether we blit the normal surface
            or the mirrored one, assuming a mirrored surface has been
            processed beforehand.
        """
        # get current value
        value = self.h_mirrored if horizontal else self.v_mirrored

        # check if state has been passed
        if state is None:
            # toggle value
            value = False if value else True
        else:
            # set value
            value = state

        # apply the new value
        if horizontal:
            self.h_mirrored = value
        else:
            self.v_mirrored = value

        # force refresh
        self.force = True

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.force = True
    
    def set_rect(self, rect, grid=False):
        x, y, w, h = rect
        
        g = self.grid_size if grid else 1
        
        self.x = x * g
        self.y = y * g
        self.w = w * g
        self.h = h * g

    def get_rect(self, grid=False):
        g = self.grid_size if grid else 1
        
        x = self.x / g
        y = self.y / g
        w = self.w / g
        h = self.h / g
        
        return (x, y, w, h)
    
    def set_pos(self, pos, grid=False):
        x, y = pos
        
        g = self.grid_size if grid else 1
        
        self.x = x * g
        self.y = y * g
        
        self.force = True
    
    def get_pos(self, grid=False):
        g = self.grid_size if grid else 1
        
        return (self.x / g, self.y / g)

    def set_size(self, size, grid=False):
        w, h = size
        
        g = self.grid_size if grid else 1
        
        self.w = w * g
        self.h = h * g

        self.force = True
    
    def get_size(self, grid=False):
        g = self.grid_size if grid else 1
        
        return (self.w / g, self.h / g)

    def set_grid_size(self, grid_size):
        self.grid_size = grid_size

    def get_center(self):
        w, h = self.get_size()
        return (w/2, h/2)

    # NOTE : recursive
    def check_force(self):
        if self.display:
            for obj in self.objects.values():
                obj.check_force()

                try:
                    if obj.force:
                        self.force = True
                except AttributeError:
                    pass

    def check_focus(self, mouse_pos):
        mx, my = mouse_pos
        x, y, w, h = self.get_rect()
            
        if (mx >= x and mx < x+w
        and my >= y and my < y+h):
            self.focused = True
        else:
            self.focused = False

    # NOTE : recursive
    def update_focus(self, mouse_pos):
        if self.display:
            # check for yourself
            self.check_focus(mouse_pos)
            
            # make mouse relative to the children
            mx, my = mouse_pos
            mouse_pos = (mx - self.x, my - self.y)
            
            for obj in self.objects.values():
                obj.update_focus(mouse_pos)

    # NOTE : recursive
    def update_state(self, mouse_but):
        clicked = max(*mouse_but)
        if self.display:
            # update self
            if self.state != "INACTIVE":
                if self.focused:
                    if clicked:
                        self.set_state("CLICKED")
                    else:
                        if self.state == "CLICKED":
                            self.emit_signal("click")
                        
                        self.set_state("MOUSEOVER")
                else:
                    self.set_state("IDLE")
            
            # update children
            for obj in self.objects.values():
                obj.update_state(mouse_but)

    def tick(self, time):
        Object.tick(self, time)

        if self.frames:
            # check if the time spent exceeded the frame delay
            if time - self.last_tick > self.frames[self.frame].delay:
                self.frames[self.frame].next()
                self.force = True

                self.last_tick = time

    def refresh(self):
        """ Refresh surface buffer with the original object's image """
        if self.surface is None:
            self.init_surface(self.get_size())
        else:
            if self.surface.get_size() != self.get_size():
                self.init_surface(self.get_size())
            else:
                self.surface.clear()
        
        if self.image:
            # define rect
            try:
                x, y = self.frames[self.frame].rect
            except KeyError:
                x, y = 0, 0

            iw, ih = self.image.get_size()
            if self.h_mode == "mirrored" and self.h_mirrored:
                x += iw/2
            if self.v_mode == "mirrored" and self.v_mirrored:
                y += ih/2

            # blit the image on the buffer
            self.surface.blit(self.image, (-x,-y))
        
        self.force = False

    # NOTE : recursive
    def render(self, surface):
        if self.display:
            # prepare surface
            if self.image is None:
                self.load()
            
            # check if refresh is forced
            if(self.surface is None
            or self.force):
                self.refresh()
            
            # render objects
            for obj in self.get_sorted_children():
                obj.render(self.surface)
            
            # apply offset
            x = self.x + self.x_offset
            y = self.y + self.y_offset
            
            # apply scaling method
            if self.scale == "scale2x":
                temp = pygame.transform.scale2x(self.surface)
            elif self.scale == "simple":
                temp = pygame.transform.scale(self.surface, (self.w*2,self.h*2) )
            else:
                temp = self.surface
            
            # blit surface on the parent
            surface.blit(temp, (x,y))

class Frame:
    def __init__(self, animation=[(0,(0,0))]):
        self.animation = animation

        self.delay = animation[0][0]
        self.rect = animation[0][1]

        self.iterator = 0

    def next(self):
        self.iterator += 1
        if self.iterator >= len(self.animation):
            self.iterator = 0

        self.delay = self.animation[self.iterator][0]
        self.rect = self.animation[self.iterator][1]

class MovingObject (Image):
    def __init__(self, name, filename=None):
        Image.__init__(self, name, filename)
        
        # movement
        self.const_vectors = {}
        self.temp_vectors = {}
        self.velocity = None
        self.fixed = False
        
        # collisions
        self.solid = False
        self.mass = 0
        self.hitboxes = []

    def make_movable(self):
        self.velocity = Vector("move", (0,0))

    def add_const_vector(self, vector):
        if not vector.name in self.const_vectors.keys():
            self.const_vectors[vector.name] = vector

    def get_const_vector(self, name):
        if name in self.const_vectors.keys():
            return self.const_vectors[name]
    
    def add_temp_vector(self, vector):
        if not vector.name in self.temp_vectors.keys():
            self.temp_vectors[vector.name] = vector

    def get_temp_vector(self, name):
        if name in self.temp_vectors.keys():
            return self.temp_vectors[name]

    def apply_vector(self, vector):
        if vector.enable:
            self.velocity += vector
    
    def apply_all_vectors(self):
        for vector in self.const_vectors.values():
            self.apply_vector(vector)
        
        for vector in self.temp_vectors.values():
            self.apply_vector(vector)
        self.temp_vectors = {}

    def move(self, vector=None):
        if not vector:
            vector = self.velocity

        if(vector and not self.fixed):
            # change the position of the object
            if vector.enable:
                x, y = vector.get_pos()
                
                # apply movement
                self.x += x
                self.y += y
                self.force = True

    # NOTE : recursive
    def move_all(self, vectors=True, move=True):
        for obj in self.objects.values():
            obj.move_all(vectors, move)
        
        if vectors:
            self.apply_all_vectors()
        
        if move:
            self.move()

class Camera (MovingObject):
    def __init__(self, name):
        MovingObject.__init__(self, name)
        
        self.active = True
        self.target = None
        self.zone = None

        self.fixed = True

    def update_vector(self):
        mx, my = self.get_center()
        cx, cy = self.target.get_center()
        px, py = self.target.get_pos()

        x = mx - (px+cx)
        y = my - (py+cy)

        self.velocity.set_pos((x, y))

    def move_all(self, vectors=True, move=True):
        if move:
            if self.active:
                # update the camera vector
                if self.target:
                    self.update_vector()

                # get the opposite of the target movement
                x = self.velocity.x
                y = self.velocity.y

                # calculate vector distance modifier
                def distance(z, z_target, priority_diff):
                    return 1.0 + (z - z_target) / (priority_diff + 1)

                children = self.get_sorted_children()
                priority_diff = children[-1].z - children[0].z
                if children:
                    for child in children:
                        d = distance(child.z, self.target.z, priority_diff)
                        # apply camera vector
                        child.move(self.velocity * d)
        
        # move children and self
        MovingObject.move_all(self, vectors, move)

class Background (MovingObject):
    def __init__(self, name, filename=None):
        MovingObject.__init__(self, name, filename)

    def duplicate(self, horizontal=True):
        # if the image is not set, we quit
        if not self.image:
            return
        
        # get the corresponding dimension
        if horizontal:
            w = self.w * 2
            h = self.h
        else:
            w = self.w
            h = self.h * 2
        
        # create a new surface
        temp = Surface((w, h))
        
        # blit self image on the new surface
        temp.blit(self.image, (0,0))
        if horizontal:
            temp.blit(self.image, (self.w, 0) )
        else:
            temp.blit(self.image, (0, self.h) )
        
        # apply the new surface
        self.image = temp
        self.surface = None
        self.w = w
        self.h = h
        
        if horizontal:
            self.h_mode = "duplicated"
        else:
            self.v_mode = "duplicated"
    
    def extend(self, color, horizontal=True):
        pass # TODO

    def move(self, vector=None):
        MovingObject.move(self, vector)
        
        if not vector:
            vector = self.velocity

        # horizontal scrolling
        if self.h_mode:
            # check direction
            if vector.x < 0: # left
                # shift background
                if(self.x + self.w / 2 <= 0):
                    self.x += self.w / 2
            elif vector.x > 0: #right
                # shift background
                if(self.x + self.w / 2 >= self.w / 2):
                    self.x -= self.w / 2

        # vertical scrolling
        if self.v_mode:
            # check direction
            if vector.y < 0: # left
                # shift background
                if(self.y + self.h / 2 <= 0):
                    self.y += self.h / 2
            elif vector.y > 0: #right
                # shift background
                if(self.y + self.h / 2 >= self.h / 2):
                    self.y -= self.h / 2

class Map (MovingObject):
    def __init__(self, name, tile_size, filename=None):
        MovingObject.__init__(self, name)
        
        self.header = []
        self.tiles = []
        self.tilesets = {}
        self.void = ""
        self.tile_size = tile_size
        self.tiles_w = 0
        self.tiles_h = 0
        
        if filename:
            self.load_from_file(filename)
    
    def load_from_file(self, filename):
        # open filename in binary format
        bstr = BinaryString(filename, 10485760) # 10 MiB
        array = bstr.array
        
        # check header and version
        if(array[:3] != b"FXP"
        or array[3] != 0):
            return
        
        # get tile palette
        i = 4
        while array[i] != 0x03:
            # get block
            if array[i] == 0x02:
                s = ""
                # read name
                for c in array[i+1:]:
                    if(c == 0x02
                    or c == 0x03):
                        break
                    else:
                        s += chr(c)
                # add the block
                self.header.append(s)
                i += len(s)
            
            i += 1
        
        # get body
        i += 1
        body = [tuple(array[c:c+2]) for c in range(i, len(array), 2)]
        
        # uncompress tiles
        line = []
        self.tiles.append(line)
        for tile in body:
            n, tileset_id = tile
            
            if n == 0:
                # create a new line
                line = []
                self.tiles.append(line)
            else:
                # fill the line
                for x in range(0, n):
                    line.append(tileset_id)
        
        # get sizes
        self.tiles_h = len(self.tiles)
        self.tiles_w = max([len(line) for line in self.tiles])

    def set_tile(self, value, pos, rel=(0,0)):
        x, y = pos
        dx, dy = rel
        
        if x+dx >= 0 and y+dy >= 0:
            try:
                self.tiles[y+dy][x+dx] = value
            except IndexError:
                return

    def get_tile(self, pos, rel=(0,0)):
        x, y = pos
        dx, dy = rel
        
        if x+dx < 0 or y+dy < 0:
            return 0
        else:
            try:
                return self.tiles[y+dy][x+dx]
            except IndexError:
                return 0

    def get_rule(self, pos):
        rule = 0x00
        
        # get upper-left (0x80)
        if self.get_tile(pos, (-1,-1)):
            rule += 0x80
        
        # get upper-middle (0x40)
        if self.get_tile(pos, (0,-1)):
            rule += 0x40
        
        # get upper-right (0x20)
        if self.get_tile(pos, (1,-1)):
            rule += 0x20
        
        # get middle-left (0x10)
        if self.get_tile(pos, (-1,0)):
            rule += 0x10
        
        # get middle-right (0x08)
        if self.get_tile(pos, (1,0)):
            rule += 0x08
        
        # get bottom-left (0x04)
        if self.get_tile(pos, (-1,1)):
            rule += 0x04
        
        # get bottom-middle (0x02)
        if self.get_tile(pos, (0,1)):
            rule += 0x02
        
        # get bottom-right (0x01)
        if self.get_tile(pos, (1,1)):
            rule += 0x01
        
        # return the rule
        return rule
    
    def set_void(self, name):
        self.void = name

    def add_tileset(self, tileset):
        self.tilesets[tileset.name] = tileset

    def update_collisions(self):
        # nested utility function
        # needed to place cursor at the right place
        def is_tested(tile):
            x, y = tile
            for hitbox in self.hitboxes:
                rx, ry, rw, rh = hitbox
                rx /= self.tile_size
                ry /= self.tile_size
                rw /= self.tile_size
                rh /= self.tile_size
                if(x >= rx and x < rx+rw
                and y >= ry and y < ry+rh):
                    return True
            
            return False
        
        tile_x = 0
        tile_y = 0
        x = 0
        y = 0
        w = 1
        h = 1
        h_end = False
        v_end = False
        # loop on each tile
        while tile_y < self.tiles_h:
            tileset_id = self.get_tile((tile_x,tile_y))
            name = self.header[tileset_id]
            # start the creation of a new rectangle
            if(name != self.void
            and self.tilesets[name].solid
            and not is_tested((tile_x,tile_y))):
                x = tile_x
                y = tile_y
                while not (h_end and v_end):
                    # test a horizontal line
                    if not h_end:
                        for cur_x in range(0, w):
                            tile = (tile_x+cur_x,tile_y+h)
                            cur_id = self.get_tile(tile)
                            cur_name = self.header[cur_id]
                            if(cur_name == self.void
                            or not self.tilesets[cur_name].solid
                            or is_tested(tile)):
                                h_end = True
                                break
                    
                    # if after the loop every tile was solid
                    if not h_end:
                        h += 1 # our rect is one tile larger
                    
                    # test a vertical line
                    if not v_end:
                        for cur_y in range(0, h):
                            tile = (tile_x+w,tile_y+cur_y)
                            cur_id = self.get_tile(tile)
                            cur_name = self.header[cur_id]
                            if(cur_name == self.void
                            or not self.tilesets[cur_name].solid
                            or is_tested(tile)):
                                v_end = True
                                break
                    
                    # if after the loop every tile was solid
                    if not v_end:
                        w += 1 # our rect is one tile larger
                
                # create a new rectangle
                ts = self.tile_size
                rect = (x*ts, y*ts, w*ts, h*ts)
                self.hitboxes.append(rect)
                x = 0
                y = 0
                w = 1
                h = 1
                h_end = False
                v_end = False
                
            # move cursor
            tile_x += w
            
            if tile_x >= self.tiles_w:
                tile_x = 0
                tile_y += 1

    def load(self):
        # create image
        self.image = Surface(self.get_size())
        
        # print tiles
        x = 0
        y = 0
        for tile_y in range(0, self.tiles_h):
            for tile_x in range(0, self.tiles_w):
                # get tile and its rule
                tileset_id = self.get_tile((tile_x,tile_y))
                name = self.header[tileset_id]
                
                # print tile
                if name != self.void:
                    rule = self.get_rule((tile_x,tile_y))
                    self.image.blit(self.tilesets[name].get_tile_by_rule(rule), (x,y))
                    x += self.tilesets[name].size
                else:
                    x += self.tile_size
                    
            # new line
            x = 0
            y += self.tile_size

class World (MovingObject):
    def __init__(self, name):
        MovingObject.__init__(self, name)
        
        # env vectors
        self.env_vectors = {}
        self.env_objects = []
        
        # collide vectors
        self.collide_vectors = {}
        self.collide_objects = []
        
        # signals
        self.add_signal("collide")
    
    def add_env_vector(self, env_name, generator):
        self.env_vectors[env_name] = generator
    
    def add_env_object(self, env_name, obj):
        self.env_objects.append((env_name,obj))

    def add_collide_vector(self, name, generator):
        self.collide_vectors[name] = generator
    
    def add_collide_object(self, vector_name, obj):
        self.collide_objects.append((vector_name,obj))
    
    def move_all(self, vectors=True, move=True):
        # apply vectors only
        MovingObject.move_all(self, vectors=True, move=False)
        
        # apply env vectors
        for env_object in self.env_objects:
            env_name, env_obj = env_object
            env_vector = self.env_vectors[env_name](env_obj)
            env_obj.apply_vector(env_vector)
        
        # get solid objects with their absolute position
        def get_solid(obj, pos, obj_list):
            ax, ay = pos
            rx, ry = obj.get_pos()
            pos = (ax+rx, ay+ry)
            if obj.solid:
                obj_list.append((obj, pos))
            
            for child in obj.objects.values():
                get_solid(child, pos, obj_list)
        
        # apply collision function
        def do_collide(obj, obstacle, rect, orect):
            collision = False
            # check for collide forces to apply
            for collide_obj in self.collide_objects:
                col_name, col_obj = collide_obj
                # apply collision to the object
                if col_obj is obj:
                    col_vector = self.collide_vectors[col_name](obj, obstacle,
                                                                rect, orect)
                    obj.apply_vector(col_vector)
                    collision = True
                # apply collision to the obstacle
                elif col_obj is obstacle:
                    col_vector = self.collide_vectors[col_name](obstacle, obj,
                                                                orect, rect)
                    obstacle.apply_vector(col_vector)
                    collision = True

            # emit collide signal
            if collision:
                self.emit_signal("collide", (obj, obstacle, col_vector))
        
        solid_list = []
        get_solid(self, self.get_pos(), solid_list)
        while len(solid_list) > 0:
            collide = False
            
            # get last object of the list (and remove it)
            obj, pos = solid_list.pop()
            ax, ay = pos # absolute pos
            
            # apply velocity to absolute positions
            if not obj.fixed:
                ax += obj.velocity.x
                ay += obj.velocity.y
            
            # try remaining objects
            for solid_obj in solid_list:
                # check collision between objects
                obstacle, opos = solid_obj
                oax, oay = opos # absolute pos
                
                # apply velocity to absolute positions
                if not obstacle.fixed:
                    oax += obstacle.velocity.x
                    oay += obstacle.velocity.y
                
                # TODO : check trajectory
                
                # loop on hitboxes
                for hitbox in obj.hitboxes:
                    x, y, w, h = hitbox
                    x += ax
                    y += ay
                    for ohitbox in obstacle.hitboxes:
                        ox, oy, ow, oh = ohitbox
                        ox += oax
                        oy += oay
                        
                        # do the test
                        if(ox >= x + w
                        or ox + ow <= x
                        or oy >= y + h
                        or oy + oh <= y):
                            pass
                        else:
                            rect = (x, y, w, h)
                            orect = (ox, oy, ow, oh)
                            # apply collision
                            do_collide(obj, obstacle, rect, orect)

        # move
        MovingObject.move_all(self, vectors=False, move=True)

class Input (Object):
    def __init__(self, name):
        Object.__init__(self, name)
        
        self.events = []
        self.keys = []
        self.mouse_pos = (0, 0)
        self.mouse_but = (0, 0, 0)
        
        # signals
        self.add_signal("quit")
        self.add_signal("keydown")
    
    def update(self):
        self.events = pygame.event.get()
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_but = pygame.mouse.get_pressed()
        
        for event in self.events:
            if event.type == pygame.QUIT:
                self.emit_signal("quit")
            if event.type == pygame.KEYDOWN:
                self.emit_signal("keydown", event.key)

    def check_key(self, key):
        return self.keys[key]


#-------------------------------------------------------------------------------
# GAME SPECIFIC
#-------------------------------------------------------------------------------

class Builder:
    def __init__(self, package):
        self.package = package

        # extract package
        # TODO

        # create objects recursively
        self.root = next(self.create_from_file(package+"/main.fxpq", type="Dimension", unique=True))

    def create_from_file(self, file, type="", unique=False):
        # parse file
        try:
            tree = ET.parse(file)
        except Exception, e:
            raise e

        # get active directory
        directory = file[:file.rfind("/")]

        # get root element
        fxpq = tree.getroot()

        # get version
        # TODO : if specs become to change in the future,
        #        manage versions to fit retro-compatibility
        version = fxpq.get("version")

        # for each object found
        for i, obj in enumerate(fxpq.findall("object")):
            # get name
            id = obj.get("id")

            # get type
            t = obj.get("type")

            # check type
            if type:
                # pass incorrect type
                if t != type:
                    continue

            # pass other objects if we wanted only one
            if unique:
                if i > 0:
                    break

            # create instance
            try:
                instance = globals()[t](id)
            except Exception, e:
                raise e

            # parse properties
            properties = obj.find("properties")
            if properties is not None:
                for p in properties:
                    if p.tag == "rect":
                        # rect property
                        x = int(p.attrib["x"])
                        y = int(p.attrib["y"])
                        w = int(p.attrib["w"])
                        h = int(p.attrib["h"])
                        instance.set_rect((x, y, w, h))
                    elif p.tag == "image":
                        # image loading
                        if p.attrib["src"]:
                            instance.load_from_file(self.package+p.attrib["src"])
                        if p.attrib["autoresize"] == "true":
                            #instance.set_size() TODO
                            pass
                    else:
                        raise Exception("The property \""+p.tag+"\" cannot be set for an object of type \"Fxp."+self.__class__.__name__+"\"")

            print(instance.get_rect())

            # parse nodes
            # TODO

            # parse scripts
            # TODO

            # parse children
            for child in obj.findall("child"):
                path = child.get("id")
                for c in self.create_from_file(directory+"/"+path+".fxpq"):
                    instance.add_child(c)

            # return object
            yield instance

class Dimension(Image):
    def __init__(self, name):
        Image.__init__(self, name)

class Zone(Image):
    def __init__(self, name):
        Image.__init__(self, name)

#-------------------------------------------------------------------------------
# USER INTERFACE
#-------------------------------------------------------------------------------

class Window (Image):
    def __init__(self, name):
        Image.__init__(self, name)
        
        self.tileset = None
        self.opened = False
        
        # create signals
        self.add_signal("close")

    def load(self):
        # open the tileset
        if not self.tileset:
            self.tileset = Tileset("window", "packages/window.png", 8)
        
        # create the surface
        self.image = Surface(self.get_size())
        
        # display corners
        w = self.w
        h = self.h
        g = self.grid_size
        self.image.blit(self.tileset.get_tile((0,0)), (0, 0)     )
        self.image.blit(self.tileset.get_tile((2,0)), (w-g, 0)   )
        self.image.blit(self.tileset.get_tile((0,2)), (0, h-g)   )
        self.image.blit(self.tileset.get_tile((2,2)), (w-g, h-g) )
        
        # display borders
        for i in range(1, (self.w / g)-1):
            self.image.blit(self.tileset.get_tile((1,0)), (i*g, 0)   )
            self.image.blit(self.tileset.get_tile((1,2)), (i*g, h-g) )
        
        for j in range(1, (self.h / g)-1):
            self.image.blit(self.tileset.get_tile((0,1)), (0, j*g)   )
            self.image.blit(self.tileset.get_tile((2,1)), (w-g, j*g) )
        
        # body
        global PALETTE
        self.image.fill(PALETTE.get_rgb("Black", "light"), (g, g, w-g*2, h-g*2) )

    def open(self):
        if not self.display:
            self.display = True
            self.opened = True
    
    def close(self):
        if self.display:
            self.display = False
            self.opened = False

    def switch(self):
        if self.opened:
            self.close()
        else:
            self.open()

class Label (Image):
    def __init__(self, name, text, color, bg_color):
        Image.__init__(self, name)
        
        self.display = True
        
        self.text = text
        self.color = color
        self.bg_color = bg_color
        
        # create signals
        # ...

    def set_text(self, text):
        self.text = text
        self.force = True
        self.load()

    def set_color(self, color, bg_color):
        if color != None:
            self.color = color
        
        if bg_color != None:
            self.bg_color = bg_color
        
        self.load()

    def load(self):
        # create text
        global PALETTE
        global FONT
        self.image = FONT.write_line(self.text)
        
        # change colors
        default_color    = PALETTE.get_rgb("White", "light")
        default_bg_color = PALETTE.get_rgb("Black", "medium")
        
        if (self.color == default_bg_color
        and self.bg_color == default_color):
            # swap front and bg
            self.image.replace_color(default_color, default_bg_color, swap=True)
        else:
            self.image.replace_color(default_color, self.color)
            self.image.replace_color(default_bg_color, self.bg_color)
        
        # set object size
        self.set_size(self.image.get_size())
        
        # change offset
        self.x_offset = 1
        self.y_offset = 1

class Button (Image):
    def __init__(self, name, text, color_name):
        Image.__init__(self, name)
        
        self.display = True
        
        self.text = text
        self.color = color_name
        self.sensitive = True
        
        # create signals
        self.add_signal("click")

    def set_state(self, state): # FIXME
        if self.state != state:
            self.state = state
            self.force = True
            self.load()

    def load(self):
        # set colors
        global PALETTE
        if self.state == "MOUSEOVER":
            border_top    = PALETTE.get_rgb(self.color, "light")
            border_bottom = PALETTE.get_rgb(self.color, "dark")
            body          = PALETTE.get_rgb(self.color, "medium")
            text_color    = PALETTE.get_rgb("White", "light")
            text_bg_color = PALETTE.get_rgb(self.color, "dark")
        elif self.state == "CLICKED":
            border_top    = PALETTE.get_rgb(self.color, "dark")
            border_bottom = PALETTE.get_rgb(self.color, "light")
            body          = PALETTE.get_rgb(self.color, "medium")
            text_color    = PALETTE.get_rgb(self.color, "dark")
            text_bg_color = PALETTE.get_rgb(self.color, "light")
        elif self.state == "INACTIVE":
            border_top    = PALETTE.get_rgb("White", "dark")
            border_bottom = PALETTE.get_rgb("White", "dark")
            body          = PALETTE.get_rgb("White", "medium")
            text_color    = PALETTE.get_rgb("Black", "light")
            text_bg_color = PALETTE.get_rgb("White", "dark")
        else:
            border_top    = PALETTE.get_rgb("White", "light")
            border_bottom = PALETTE.get_rgb("White", "dark")
            body          = PALETTE.get_rgb("White", "medium")
            text_color    = PALETTE.get_rgb(self.color, "dark")
            text_bg_color = PALETTE.get_rgb("White", "light")
        
        # get font size
        global FONT
        text_size = (len(self.text) * FONT.size) + 1 # text is one pixel away from the border
        
        # calculate size of the button
        w = ((text_size / self.grid_size) + 1) * self.grid_size # we round to the grid
        h = self.grid_size
        self.set_size((w + 2, h + 2))
        
        # prepare surface
        # the surface is one pixel larger for every border
        self.image = Surface((w+2, h+2))
        # this is the real position of the button on the surface
        x = 1
        y = 1
        # we must blit the surface one pixel back
        self.x_offset = -1
        self.y_offset = -1
        
        # render body
        self.image.fill(body, [x, y, w, h])
        pygame.draw.line(self.image, border_top,    (x, y-1), (x+w-1, y-1) )
        pygame.draw.line(self.image, border_top,    (x-1, y), (x-1, y+h-1) )
        pygame.draw.line(self.image, border_bottom, (x, y+h), (x+w-1, y+h) )
        pygame.draw.line(self.image, border_bottom, (x+w, y), (x+w, y+h-1) )
        
        # render text
        label_name = "button_label"
        label = Label(label_name, self.text, text_color, text_bg_color)
        label.set_pos((x, y))
        if label_name in self.objects:
            self.objects[label_name] = label
        else:
            self.add_child(label)
        
        # move the text one pixel to the right if clicked
        if self.state == "CLICKED":
            label.set_pos((x+1, y))
        else:
            label.set_pos((x, y))

class Separator (Image):
    def __init__(self, name, vertical=False):
        Image.__init__(self, name)
        
        self.display = True
        self.sensitive = True

    def set_state(self, state): # FIXME
        if self.state != state:
            self.state = state
            self.force = True
            self.load()

    def load(self):
        # set colors
        global PALETTE
        border_top    = PALETTE.get_rgb("Black", "medium")
        border_bottom = PALETTE.get_rgb("White", "dark")
        
        # positions
        x = 1
        y = 3
        w = self.w
        h = self.h
        
        # render
        self.image = Surface((w, h))
        self.image.fill(0)
        pygame.draw.line(self.image, border_top,    (x, y), (x+w-4, y) )
        pygame.draw.line(self.image, border_bottom, (x+1, y+1), (x+w-3, y+1) )


#-------------------------------------------------------------------------------
# PIXEL MANAGEMENT
#-------------------------------------------------------------------------------

class Tileset:
    def __init__(self, name, filename, size):
        self.name = name
        self.tiles = []
        self.rules = {}
        self.size = size
        self.image = pygame.image.load(filename)
        self.solid = False
        
        # parse image
        self.w = self.image.get_width() / size
        self.h = self.image.get_height() / size
        for j in range(0, self.h):
            for i in range(0, self.w):
                temp = Surface((size, size))
                temp.blit(self.image, (0,0), (i*size, j*size, size, size) )
                self.tiles.append(temp)

    def add_rule(self, name, tile, flag, mask=0xFF):
        self.rules[name] = (tile, flag, mask)

    def get_tile(self, pos):
        x, y = pos
        index = y * self.w + x
        
        return self.tiles[index]

    def get_tile_by_rule(self, flag):
        for rule in self.rules.values():
            tile, rule_flag, rule_mask = rule
            if rule_flag & rule_mask == flag & rule_mask:
                return self.get_tile(tile)
        
        # if nothing returned yet
        return self.get_tile((0,0))

class Color:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def set_rgb(self, tone, rgb):
        self.values[tone] = rgb

    def get_rgb(self, tone):
        if tone in self.values.keys():
            return self.values[tone]

class Palette:
    def __init__(self, name):
        self.name = name
        self.colors = {}
        self.colorkey = (0, 0, 0)
        self.default = None

    def append(self, color):
        if not color.name in self.colors.keys():
            self.colors[color.name] = color

    def change_tone(self, name, tone, rgb):
        if name in self.colors.keys():
            self.colors[name].set_rgb(tone, rgb)

    def set_colorkey(self, rgb):
        self.colorkey = rgb

    def get_colorkey(self):
        return self.colorkey

    def set_default(self, colorname):
        self.default = colorname

    def get_rgb(self, name, tone):
        if name in self.colors.keys():
            return self.colors[name].get_rgb(tone)
        else:
            if self.default:
                return self.colors[self.default].get_rgb(tone)
            else:
                return self.colorkey

    def get_all_rgb(self):
        result = [self.colorkey]
        for color in self.colors.values():
            for tone in color.values.keys():
                result.append(color.get_rgb(tone))
        
        return result

class Font:
    def __init__(self, filename, size):
        self.chars = {}
        self.filename = filename
        self.size = size
        
        # open image file
        image = pygame.image.load(filename)
        
        # parse file
        rect_x = 0
        rect_y = 0
        for i in range(0x20, 0x7F, 0x01): # ASCII
            if (i - 0x20) % 16 == 0 and i - 0x20 > 0:
                rect_y += size
                rect_x = 0
            
            temp = Surface((size, size))
            temp.blit(image, (0,0), (rect_x, rect_y, size, size) )
            self.chars[chr(i)] = temp
            
            rect_x += size

    def write_line(self, text):
        # create a big enough surface
        h = self.size
        w = self.size * len(text)
        
        surface = Surface((w, h))
        
        # paste the chars
        x = 0
        for c in text:
            surface.blit(self.chars[c], (x, 0) )
            x += self.size
        
        # return the surface
        return surface

class Surface (pygame.Surface):
    def __init__(self, size):
        pygame.Surface.__init__(self, size)
        
        # init
        global PALETTE
        self.set_palette(PALETTE.get_all_rgb())
        self.set_colorkey(PALETTE.get_colorkey())
        self.fill(PALETTE.get_colorkey())

    def clear(self):
        global PALETTE
        self.fill(PALETTE.get_colorkey())

    def replace_color(self, old_rgb, new_rgb, swap=False):
        palette = [color for color in self.get_palette()]
        try:
            oi = palette.index(old_rgb)
            if swap: ni = palette.index(new_rgb)
        except ValueError:
            return
        
        palette[oi] = new_rgb
        if swap: palette[ni] = old_rgb
        self.set_palette(palette)

#-------------------------------------------------------------------------------
# FILE I/O
#-------------------------------------------------------------------------------

class BinaryString:
    def __init__(self, filename, max_size):
        # load raw binary data
        f = open(filename, "rb")
        
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        
        if size <= max_size:
            string = f.read()
        
        f.close()
        
        # convert string to binary integers
        self.array = bytearray(string, "ascii")

#-------------------------------------------------------------------------------
# BUILT-IN FUNCTIONS
#-------------------------------------------------------------------------------

# built-in physics
def simple_repulsion(obj, obstacle, rect, orect):
    vx, vy = obj.velocity.get_pos()
    rx, ry = 0, 0
    
    # make sure the objects do not intersect
    x, y, w, h = rect
    ox, oy, ow, oh = orect
    
    cx = x+w/2 # center
    cy = y+h/2
    ocx = ox+ow/2 # obstacle center
    ocy = oy+oh/2
    
    xsize = (w/2)+(ow/2)
    ysize = (h/2)+(oh/2)
    
    xdiff = cx - ocx
    ydiff = cy - ocy
    
    xrep = xsize - abs(xdiff)
    yrep = ysize - abs(ydiff)
    
    if xrep <= yrep and xrep > 0:
        if xdiff >= 0:
            rx += xrep
        else:
            rx -= xrep
    elif yrep <= xrep and yrep > 0:
        if ydiff >= 0:
            ry += yrep
        else:
            ry -= yrep
    
    # apply bounce and friction
    # TODO
    
    # create repulsion vector
    repulsion = Vector()
    repulsion.set_pos((rx,ry))
    
    return repulsion


