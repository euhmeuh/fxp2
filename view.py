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

import fxplib as Fxp

import time
import copy

class Gauge(Fxp.Image):
    def __init__(self, name):
        # attributes
        self.life_amount = 1.0
        self.mana_amount = 1.0

        self.life = None
        self.mana = None

        # init surface
        Fxp.Image.__init__(self, name)
        self.init_surface((72,95))

        # load gauges
        gauges = Fxp.Image("gauges", "packages/gauges.png")

        # load fluids
        self.life = Fxp.Image("fluid_life", "packages/gauges_fluid.png")
        self.life.set_pos((9,23))
        self.life.set_size((22,44))

        self.mana = Fxp.Image("fluid_mana", "packages/gauges_fluid.png")
        self.mana.set_pos((41,31))
        self.mana.set_size((22,44))
        self.mana.image.replace_color(Fxp.PALETTE.get_rgb("Red", "medium"),
                                      Fxp.PALETTE.get_rgb("Blue", "medium"))
        self.mana.image.replace_color(Fxp.PALETTE.get_rgb("Red", "dark"),
                                      Fxp.PALETTE.get_rgb("Blue", "dark"))

        # set fluid animation
        fluid_frames = {}

        fluid_frames["empty"] = Fxp.Frame((
            (1000, (0,0)),
            ))

        fluid_frames["full"] = Fxp.Frame((
            (200, (22,0)),
            (200, (44,0)),
            (200, (66,0)),
            (200, (88,0)),
            ))

        self.life.frames = fluid_frames
        self.life.frame = "full"

        self.mana.frames = copy.deepcopy(fluid_frames)
        self.mana.frame = "full"

        # load text
        self.life_text = Fxp.Label("label_life", "{}%".format(int(self.life_amount*100)),
                                   Fxp.PALETTE.get_rgb("White", "light"),
                                   Fxp.PALETTE.get_rgb("Black", "medium"))
        self.life_text.set_pos((7,4))

        self.mana_text = Fxp.Label("label_mana", "{}%".format(int(self.life_amount*100)),
                                   Fxp.PALETTE.get_rgb("White", "light"),
                                   Fxp.PALETTE.get_rgb("Black", "medium"))
        self.mana_text.set_pos((39,9))

        # priorities
        self.life.z = -1.0
        self.mana.z = -1.0

        # pack
        self.add_child(gauges)
        self.add_child(self.life)
        self.add_child(self.life_text)
        self.add_child(self.mana)
        self.add_child(self.mana_text)

    def check_force(self):
        self.check_amount("life")
        self.check_amount("mana")

        # update text
        self.life_text.set_text("{}%".format(int(self.life_amount*100)))
        self.mana_text.set_text("{}%".format(int(self.mana_amount*100)))

        # render
        Fxp.Image.check_force(self)

    def check_amount(self, fluid):
        # TODO : remove these magic numbers
        lw, lh = 22, 44

        amount = self.life_amount if fluid == "life" else self.mana_amount
        obj = self.life if fluid == "life" else self.mana

        # check amount
        if amount <= 0:
            amount = 0.0
            obj.y_offset = 0
            obj.set_size((lw, lh))
            obj.frame = "empty"
        elif amount <= 1:
            obj.y_offset = (lh-7) - ((lh - 7) * amount)
            obj.set_size((lw,lh - obj.y_offset))
            obj.frame = "full"
        else:
            amount = 1.0
            obj.y_offset = 0
            obj.set_size((lw, lh))
            obj.frame = "full"

        if fluid == "life":
            self.life_amount = amount
        else:
            self.mana_amount = amount

class View:
    def __init__(self, model, size, scale_mode=None, fullscreen=False):
        self.model = model
        
        # screen size and options
        w, h = size
        if (scale_mode == "scale2x"
        or  scale_mode == "simple"):
            w *= 2
            h *= 2
        
        self.flags = 0
        if fullscreen:
            self.flags |= Fxp.pygame.FULLSCREEN
        
        self.size = self.width, self.height = (w, h)
        self.grid_size = 8
        self.scale = scale_mode
        self.screen = Fxp.pygame.display.set_mode(self.size, self.flags, 8)
        self.framerate = 60
        self.clock = Fxp.pygame.time.Clock()
        self.root = None
        
        while not Fxp.pygame.display.get_active():
            time.sleep(0.1)
        
        Fxp.pygame.display.set_caption("Final Experience 2")
        Fxp.pygame.mouse.set_visible(False)
        
        # color palette
        Fxp.PALETTE = self.model.get_palette("packages/Manafia/palettes/rilouw.pal")
        
        # create a font
        Fxp.FONT = Fxp.Font("packages/font.png", 6)
        
        # prepare screen
        self.screen.set_palette(Fxp.PALETTE.get_all_rgb())
        self.screen.set_colorkey(Fxp.PALETTE.colorkey)
        self.screen.fill(Fxp.PALETTE.get_rgb("Black", "dark"))

    def load_title(self):
        # create the input devices
        inputdev = Fxp.Input("inputdev")

        # create the gui layer
        gui = Fxp.Image("gui")
        gui.set_size(self.get_size())
        gui.init_surface(self.get_size())
        
        # create mouse cursor
        cursor = Fxp.Image("cursor", "packages/cursor.png")

        # create the root container
        builder = Fxp.Builder("packages/_Title")
        root = builder.root
        root.load_from_solid_color(Fxp.PALETTE.get_rgb("White", "light"),
                                   (self.get_width(), self.get_height()))
        root.scale = self.scale

        # define priorities
        gui.z = 1
        cursor.z = 10

        # pack objects
        gui.add_child(cursor)
        
        root.add_child(inputdev)
        root.add_child(gui)
        
        # send the root container
        self.root = root

    def load_game(self):
        # create the gui layer
        gui = Fxp.Image("gui")
        gui.set_size(self.get_size())
        gui.init_surface(self.get_size())
        
        # create the input devices
        inputdev = Fxp.Input("inputdev")
        
        # create a camera
        camera = Fxp.Camera("camera")
        camera.set_size(self.get_size())
        camera.init_surface(self.get_size())
        camera.make_movable()
        
        # create physics world
        world = Fxp.World("world")
        world.set_size(self.get_size())
        world.init_surface(self.get_size())
        world.display = True
        
        # game horizon
        horizon = Fxp.Image("horizon")
        horizon.load_from_solid_color(Fxp.PALETTE.get_rgb("Cyan", "light"), self.get_size())
        
        # create moutains background
        mountain1 = Fxp.Background("mountain1")
        mountain1.load_from_file("packages/Manafia/maps/Golfia/mountain1.png")
        mountain1.duplicate()
        mountain1.make_movable()
        
        mountain2 = Fxp.Background("mountain2")
        mountain2.load_from_file("packages/Manafia/maps/Golfia/mountain2.png")
        mountain2.duplicate()
        mountain2.make_movable()
        
        # create clouds
        cloud1 = Fxp.MovingObject("cloud1")
        cloud1.load_from_file("packages/Manafia/maps/Golfia/cloud1.png")
        cloud1.set_pos((16,-16))
        cloud1.make_movable()
        
        cloud2 = Fxp.MovingObject("cloud2")
        cloud2.load_from_file("packages/Manafia/maps/Golfia/cloud2.png")
        cloud2.set_pos((384,-32))
        cloud2.make_movable()
        
        # ground
        ground1 = Fxp.Background("ground1")
        ground1.load_from_file("packages/Manafia/~temp/ground1.png")
        ground1.duplicate()
        ground1.make_movable()
        
        dirt = Fxp.Tileset("dirt", "packages/Manafia/maps/Golfia/dirt.png", 16)
        dirt.solid = True
        dirt.add_rule("ul", (0,0), 0x2F, mask=0xDB)
        dirt.add_rule("um", (1,0), 0xBF, mask=0x5F)
        dirt.add_rule("ur", (2,0), 0x97, mask=0x7E)
        dirt.add_rule("ml", (0,1), 0xEF, mask=0x7B)
        dirt.add_rule("mm", (1,1), 0xFF)
        dirt.add_rule("mr", (2,1), 0xF7, mask=0xDE)
        dirt.add_rule("bl", (0,2), 0xE9, mask=0x7E)
        dirt.add_rule("bm", (1,2), 0xFD, mask=0xFA)
        dirt.add_rule("br", (2,2), 0xF4, mask=0xDB)
        dirt.add_rule("cbr", (3,0), 0xFE)
        dirt.add_rule("cbl", (4,0), 0xFB)
        dirt.add_rule("cur", (3,1), 0xDF)
        dirt.add_rule("cul", (4,1), 0x7F)
        dirt.add_rule("cdr", (3,2), 0xDB)
        dirt.add_rule("cdl", (4,2), 0x7E)
        ground2 = Fxp.Map("ground2", 16, "packages/Manafia/maps/Golfia/golfia.map")
        ground2.set_size((self.get_width(), self.get_height()))
        ground2.set_void("air")
        ground2.add_tileset(dirt)
        ground2.make_movable()
        ground2.solid = True
        
        # FIXME this is a test
#        ground2.set_tile(0, (12,18))
#        ground2.set_tile(0, (12,18), (1,0))
#        ground2.set_tile(0, (12,18), (0,1))
#        ground2.set_tile(0, (12,18), (1,1))
#        ground2.set_tile(0, (16,17))
        
        # FIXME (remove me)
        ground2.update_collisions()
#        loop = 0
#        for hitbox in ground2.hitboxes:
#            rx, ry, rw, rh = hitbox
#            robj = Fxp.Image("obj"+str(loop))
#            robj.load_from_solid_color(Fxp.PALETTE.get_rgb("Red", "light"), (rw-4,rh-4))
#            robj.set_pos((rx+2,ry+2))
#            ground2.add_child(robj)
#            loop += 1

        # I'd like to be a tree !
        tree = Fxp.MovingObject("tree")
        tree.load_from_file("packages/Manafia/maps/Golfia/tree.png")
        tree.set_pos((272,96))
        tree.make_movable()
        tree.solid = True
        tree.hitboxes.append((18,6,40,1))

        # portals, now we're getting serious...
        portal = Fxp.MovingObject("portal")
        portal.load_from_file('packages/Manafia/maps/Golfia/portal.png')
        portal.set_pos((112,96))
        portal.set_size((160,160))

        portal_frames = {}

        portal_frames["idle"] = Fxp.Frame((
            (200, (0,0)),
            (200, (160,0)),
            (200, (160*2,0)),
            (200, (160*3,0)),
            (200, (160*4,0)),
            (200, (160*5,0)),
            (200, (160*6,0)),
            (200, (160*7,0))
            ))

        portal.frames = portal_frames
        portal.frame = "idle"
        
        # character
        character = Fxp.MovingObject("character")
        character.load_from_file("packages/Manafia/common/euhmeuh.png")
        character.set_size((42,46))
        character.set_pos((235,169))
        character.mirror(rect=(42,46))
        character.make_movable()
        character.solid = True
        character.hitboxes.append((13,16,25,30))

        char_frames = {}

        char_frames["idle"] = Fxp.Frame((
            (100, (0,0)),
            (100, (42,0)),
            (200, (42*2,0)),
            (100, (42*3,0)),
            (100, (42*4,0)),
            (100, (42*5,0))
            ))

        char_frames["run"] = Fxp.Frame((
            (100, (0,46)),
            (100, (42,46)),
            (100, (42*2,46)),
            (150, (42*3,46)),
            (100, (42*4,46)),
            (100, (42*5,46)),
            (100, (42*6,46)),
            (150, (42*7,46))
            ))

        character.frames = char_frames
        character.frame = "idle"

        # ennemy !
        ennemy = Fxp.MovingObject("ennemy")
        ennemy.load_from_file("packages/Manafia/common/base.png")
        ennemy.set_size((42,46))
        ennemy.set_pos((235,119))
        ennemy.mirror(rect=(42,46))
        ennemy.make_movable()
        ennemy.solid = True
        ennemy.hitboxes.append((13,16,25,30))

        ennemy.frames = copy.deepcopy(char_frames)
        ennemy.frame = "idle"
                
        # create buttons   
        text_option     = "        Options       "
        text_disconnect = "  Return to main menu "
        text_quit       = "     Quit the game    "
        button_options = Fxp.Button("button_options", text_option, "Blue")
        button_options.set_grid_size(self.grid_size)
        button_options.set_pos((2,2), grid=True)
        button_options.set_state("INACTIVE")
        
        separator = Fxp.Separator("separator")
        separator.set_grid_size(self.grid_size)
        separator.set_rect((1,4,19,1), grid=True)
        
        button_disconnect = Fxp.Button("button_disconnect", text_disconnect, "Orange")
        button_disconnect.set_grid_size(self.grid_size)
        button_disconnect.set_pos((2,6), grid=True)
        
        button_quit = Fxp.Button("button_quit", text_quit, "Red")
        button_quit.set_grid_size(self.grid_size)
        button_quit.set_pos((2,8), grid=True)
        
        # create mouse cursor
        cursor = Fxp.Image("cursor", "packages/cursor.png")

        # create life and mana gauges
        gauge = Gauge("gauge")
        gauge.set_rect((0,289,72,95))
        
        # create a window
        window = Fxp.Window("window")
        window.set_grid_size(self.grid_size)
        window.set_rect((21,8,21,11), grid=True)
        window.display = False
        
        # fps counter
        label_fps = Fxp.Label("label_fps", "00",
                              Fxp.PALETTE.get_rgb("Black", "light"),
                              Fxp.PALETTE.get_rgb("Cyan", "dark"))
        
        # create the root container
        root = Fxp.Image("root")
        root.load_from_solid_color(Fxp.PALETTE.get_rgb("White", "light"),
                                   (self.get_width(), self.get_height()))
        root.scale = self.scale
        
        # create forces
        force_wind = Fxp.Vector("wind", (0.035,1))
        gravity = Fxp.Vector("gravity", (0.5,0.5))
        
        # apply forces
        #cloud1.add_const_vector(force_wind)
        #cloud2.add_const_vector(force_wind)
        character.add_const_vector(gravity)
        ennemy.add_const_vector(gravity)
        
        # add world air friction
        def create_air_friction(obj):
            velocity = obj.velocity
            friction = - velocity * 0.05
            return friction
        
        world.add_env_vector("air_friction", create_air_friction)
        world.add_env_object("air_friction", character)
        world.add_env_object("air_friction", ennemy)
        world.add_env_object("air_friction", cloud1)
        world.add_env_object("air_friction", cloud2)
        
        world.add_collide_vector("repulsion", Fxp.simple_repulsion)
        world.add_collide_object("repulsion", character)
        world.add_collide_object("repulsion", ennemy)
        
        # define priorities
        horizon.z     = -1.0
        camera.z      = 0.0
        mountain1.z   = -4.0
        mountain2.z   = -3.0
        cloud1.z      = -2.0
        cloud2.z      = -3.5
        ground1.z     = -1.0
        portal.z      = 0.0
        ground2.z     = 0.001
        character.z   = 0.001
        ennemy.z      = 0.001
        tree.z        = 0.002
        gui.z         = 1.0
        world.z       = 0.0
        window.z      = 0.0
        button_options.z    = 1.0
        separator.z         = 1.0
        button_disconnect.z = 1.0
        button_quit.z       = 1.0
        label_fps.z   = 9.0
        cursor.z      = 10.0
        
        # define camera target
        camera.target = character
        camera.z_dist = 30
        #camera.zone = (128,128,256,128)
        
        # pack objects
        camera.add_child(mountain1)
        camera.add_child(mountain2)
        camera.add_child(cloud1)
        camera.add_child(cloud2)
        camera.add_child(ground1)
        camera.add_child(ground2)
        camera.add_child(tree)
        camera.add_child(portal)
        camera.add_child(character)
        camera.add_child(ennemy)
        
        world.add_child(camera)
        
        window.add_child(button_options)
        window.add_child(separator)
        window.add_child(button_disconnect)
        window.add_child(button_quit)
        gui.add_child(window)
        gui.add_child(label_fps)
        gui.add_child(cursor)
        gui.add_child(gauge)
        
        root.add_child(horizon)
        root.add_child(world)
        root.add_child(gui)
        root.add_child(inputdev)
        
        # give the controller access to the root object
        self.root = root

    def get_width(self):
        if self.is_scale():
            return self.width / 2
        else:
            return self.width

    def get_height(self):
        if self.is_scale():
            return self.height / 2
        else:
            return self.height
    
    def get_size(self):
        if self.is_scale():
            return (self.width / 2, self.height / 2)
        else:
            return (self.width, self.height)

    def is_scale(self):
        if (self.scale == "scale2x"
        or  self.scale == "simple"):
            return True
        else:
            return False

    def refresh(self):
        self.clock.tick(self.framerate)
        
        # update fps
        fps = self.root.get_child("gui/label_fps")
        if fps: fps.set_text(str(self.clock.get_fps()))
        
        # tick objects
        self.root.tick(Fxp.pygame.time.get_ticks())

        # render all objects
        self.render_all()
        
        # flip screen
        Fxp.pygame.display.flip()

    def render_all(self):
        self.root.render(self.screen)

