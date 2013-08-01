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

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        self.quit = False
        self.root = None
    
    def load_title(self):
        # load view
        self.view.load_title()
        self.root = self.view.root
        
        inputdev = self.root.get_child("inputdev")
        inputdev.connect_signal("quit", self.on_title_input_quit)
        inputdev.connect_signal("keydown", self.on_title_input_keydown)

    def load_game(self):
        # load view
        self.view.load_game()
        self.root = self.view.root
        
        # options
        speed = 0.30
        self.VECTOR_UP    = Fxp.Vector("up",   (10,-0.5))
        self.VECTOR_LEFT  = Fxp.Vector("left",   (speed,1))
        self.VECTOR_RIGHT = Fxp.Vector("right", (speed,0))
        #Fxp.pygame.key.set_repeat(30, 30)
        
        # get objects and connect signals
        button_disconnect = self.root.get_child("gui/window/button_disconnect")
        button_options    = self.root.get_child("gui/window/button_options")
        button_quit       = self.root.get_child("gui/window/button_quit")
        world        = self.root.get_child("world")
        inputdev     = self.root.get_child("inputdev")
        
        button_disconnect.connect_signal("click", self.on_button_disconnect_click)
        button_options.connect_signal("click", self.on_button_options_click)
        button_quit.connect_signal("click", self.on_button_quit_click)
        
        world.connect_signal("collide", self.on_world_collide)
        
        inputdev.connect_signal("quit", self.on_game_input_quit)
        inputdev.connect_signal("keydown", self.on_game_input_keydown)
    
    # execute a new program loop
    def loop(self):
        while not self.quit and self.root:
            # update events
            inputdev = self.root.get_child("inputdev")
            inputdev.update()
            
            mouse_pos = inputdev.mouse_pos
            
            if(self.view.scale == "simple"
            or self.view.scale == "scale2x"):
                mouse_pos = (mouse_pos[0] / 2, mouse_pos[1] / 2)
            
            # test keys
            character = self.root.get_child("world/character")
            if character:
                character.frame = "idle"
                if inputdev.check_key(Fxp.pygame.K_q):
                    character.apply_vector(self.VECTOR_LEFT)
                    character.flip(state=True)
                    character.frame = "run"
                if inputdev.check_key(Fxp.pygame.K_d):
                    character.apply_vector(self.VECTOR_RIGHT)
                    character.flip(state=False)
                    character.frame = "run"
            
            # update cursor position
            cursor = self.root.get_child("gui/cursor")
            if cursor: cursor.set_pos(mouse_pos)
            
            # update focus
            self.root.update_focus(mouse_pos)
            
            # change states and emit signals
            gui = self.root.get_child("gui")
            if gui: gui.update_state(inputdev.mouse_but)
            
            # move objects
            self.root.move_all()
            
            # check objects refresh
            self.root.check_force()
            
            # execute signals
            self.root.execute_signals()
            
            # refresh screen
            self.view.refresh()

    def quit_loop(self):
        self.quit = True

    def on_title_input_quit(self, obj, response=None, data=None):
        self.quit_loop()
    
    def on_title_input_keydown(self, obj, response=None, data=None):
        key = response
        if key == Fxp.pygame.K_ESCAPE:
            self.quit_loop()
        if key == Fxp.pygame.K_RETURN:
            self.load_game()

    def on_game_input_quit(self, obj, response=None, data=None):
        self.quit_loop()
    
    def on_game_input_keydown(self, obj, response=None, data=None):
        key = response
        if key == Fxp.pygame.K_ESCAPE:
            window = self.root.get_child("gui/window")
            window.switch()
        if key == Fxp.pygame.K_f:
            character = self.root.get_child("world/character")
            camera = self.root.get_child("world/camera")
            if camera.active:
                character.fixed = False
                camera.active = False
            else:
                character.fixed = True
                camera.active = True
        if key == Fxp.pygame.K_z:
            self.root.get_child("world/character").apply_vector(self.VECTOR_UP)

    def on_button_disconnect_click(self, obj, response=None, data=None):
        self.load_title()

    def on_button_options_click(self, obj, response=None, data=None):
        print("You clicked on the \"options\" button.")

    def on_button_quit_click(self, obj, response=None, data=None):
        self.quit_loop()
    
    def on_world_collide(self, obj, response=None, data=None):
        obj1, obj2 = response
        #print(obj1.name, obj2.name)
    


