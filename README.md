fxp2
====

Final Experience 2 - Multiplayer platform RPG

FXP2 is a fast-paced platform action RPG taking the best from fighting, adventure and platform games, mixing it into a wonderful pixelart world.

The game works on **Linux**, **MacOS** and **Windows**. It is coded mainly in **Python**, with the help of **Pygame**, which uses **SDL** (shout-outs to these three communities, you guys rock!).

The game is released under the terms of the GNU General Public License version 3 (GPLv3). See COPYING for the terms. It is free (as in free beer), a free software (as in free speech), and it is open-source.
 
The game is driven by three concepts : Play, Create and Share.
You can play and have fun with others, but you can also create your own world and invite your friends to discover it. 
Everyone can host a server and share his universe.

[→ Jump to programming details](#technical-stuff)

> **Note :**  
> The game is currently in development, so a lot of the functionalities presented here are not implemented yet.  
> Some elements are likely to change during the development.

Play
----

### Create your character

Select between 3 races :
 - **Humans**, peaceful peasants or fearless warriors, they settled and raised *Golfia*, the cosmopolitan capital of *Manafia*.
 - **Exhumed**, undead humans raised by an evil force, they lost the war against humans and have been exiled into the earth.
 - **Aleph**, aliens who came from outer-space, attracted by the powerful energy emanating from *Manafia*.

### Choose your style

Learn hundreds of spells divided into multiple classes.
Each race has 3 classes, but other "special classes" are hidden in the world, awaiting for you to learn them.
 - Humans can be *Warriors*, *Mages* or *Alchemists*.
 - Exhumed can be *Shadows*, *Gravediggers* or *Fleshrippers*.
 - Aleph can be *Shamans*, *Climbers* or *Spitters*.
 
When your character is created, you must choose one of the three classes of your race.
When it reaches the level 30, you can choose another class, including a special one if you find the corresponding quest.
The same applies to the level 60.
You can have a maximum of three classes.

### Fight monsters or other players in real time

Fights are dynamic and fast-paced. You can play with a keyboard and a mouse, but a gamepad is also a good idea.
In fact, special moves are executed by making combos like the good old fighting games (remember the Hadoken ?).
 
During your adventures, you will face lots of monsters you can fight alone or within a party.
You can also fight against other parties, to prove the world your the most skilled player (or just beat the cr\*p out of somebody you don't like).
 
Parties can have a maximum of 6 players. You read that : you can have fights with 12 players casting spells at each other!

### Fulfill your adventurer's dreams

Take parts into quests, explore dungeons and acquire treasures and magical stuff.
But be careful! The more powerful the artifact is, the more protected and hidden it will be.

### Have fun with other players

Apart from the main events, you can visit the different cities. They are full of things to do :
 - Buy equipment and utility objects in the shops.
 - Play minigames in the bars.
 - Create your own guild.
 - Take part into the economic war between the Merchants and the Thieves.
 
And much more...

Create
------

Playing a game is great, but you will finally get to the point where you know everything. Where your rank on the official forum is "Great Master and Moderator" and you can't count the number of soda cans you spent playing in the night.
When you reached this situation, you're craving for more, and wish you could be a developer and add content to the game.
Because our developer team and I found ourselves in this situation a lot more than we thought, we wanted to create a game where the player can create new content.
This is why FXP2 comes with a level editor included.
 
You can create your own "dimension", that contains different zones, cities, dungeons, original quests, monsters and objects.
You can create everything from the pixelart graphics to the world physics rules (yes, you can make a dungeon on the moon, with a different gravity).

You don't need to know how to code, because everything is made with an easy-to-use user interface.
Although, if you know how to code in Python (which is not a difficult language), you can add Python scripts inside the game to have a fine-grained control over entities' behavior.

You also don't need to know how to draw, as you can use pre-made graphics from the game, or made by the community.
But if it happens that you know how to draw, especially pixelart, then you can have a lot of fun creating your very own environments, monsters and objects, and see them come to life with a few simple clicks.

Share
-----

When your story is written, when your *dimension* is ready to be played, you can share it with your friends on a local network, or over the Internet.
You just need to start your own server on your computer and give your IP address to your friends, or register to the "master server" and give them the name of your server.
 
This is actually the trickiest part, because you'll need to configure your Internet "box" to let your friends enter.
But if you can get over this obstacle (and a lot of people will be there to help you), then you will be able to play your *dimension* with friends!
 
This is for us the most important point about playing video games, and we're doing everything to make this happening, because games are meant to be played with others.

Technical stuff
---------------

### Contact

If your interested in participating to the development, feel free.
You can report bugs, submit patches or even write documentation (but I doubt someone's gonna choose the later).
 
We are currently putting up a website, which will permit to get in touch with other people working on the game.
An IRC chat and a mailing list are also planned.

Links will be added soon... (TODO)

### Code architecture

#### Files

The code is composed of very few files :

| File          |Type              | Description / Usage                                                  |
|---------------|------------------|----------------------------------------------------------------------|
| fxp2.py       | Starter file     | Launch the game                                                      |
| view.py       | View layer       | Manage how things are displayed on screen                            |
| model.py      | Model layer      | Define the logic and the gameplay of the game                        |
| controller.py | Controller layer | Make the `model` and the `view` work together and process user input |
| fxplib.py     | Core engine      | Provide game features like a display system or a physic engine       |

#### How it works

The game starts by running *fxp2.py*, which creates a `view`, a `model` and a `controller`.  
Then *fxp2.py* calls `load_title()` from the `controller` to load the title screen.  
After that, *fxp2.py* calls `controller.loop()` to start the game loop.  
 
The game will run until the `controller` calls `quit_loop()`.

[→ Visit the wiki for further details](https://github.com/euhmeuh/fxp2/wiki)
