# Rover Ready

Rutgers Virtual Reality & Lab  
Project 2 Proposal Presentation  
Group Members: Chirag Baviskar and Dhrumil Patel

---

## Slide 1 - Project Overview

- The player restores a damaged rover before deployment
- Main tasks are inserting power modules and repairing damaged parts
- The player interacts with the rover directly using the controllers

> Our project is called Rover Ready. It is a small VR repair experience set in a single garage bay. The basic goal is simple: get a damaged rover working again before it can leave.

---

## Slide 2 - Why This Works in VR

- Grabbing and inserting parts works better in VR than on a normal screen
- Repairing rover parts feels more direct when the player uses hand motions
- The player can see the rover change as each step is completed
- A one-room project is realistic for a 2-person team and easier to finish well

> We think VR makes sense for this because the whole experience is based on reaching out, grabbing parts, putting them in place, and using a tool on the rover. That feels a lot more natural in VR than it would on a normal screen. Since the whole project is one room with two main interactions, it is also something we can realistically finish.

---

## Slide 3 - Scene and Art Direction

Scene Setup

- One compact rover repair bay
- Rover, charging rack, tool wall, floor markings
- A few damaged rover parts placed around the main work area
- All major objects stay within easy reach of the player

Art Direction

- Low-poly industrial look
- Simple materials and a limited color palette
- Custom assets: power module and repair tool
- Color contrast can help show powered, damaged, and repaired states

> The scene is one small repair bay with the rover in the middle. Around it, we have the charging rack, the tool wall, and the damaged rover parts the player has to work on. We are also using a low-poly industrial style so the scene stays manageable to build and still looks consistent.

---

## Slide 4 - Interaction Loop

1. Pick up a power module from the rack
2. Insert it into the rover and power it on
3. Pick up the repair tool and fix damaged rover parts
4. The rover lights up and becomes ready to go
5. Later repair jobs get harder as the game continues

> The interaction loop starts simple. First, the player grabs a power module and inserts it into the rover, which powers it on. After that, the player uses the repair tool on the damaged rover parts, and the rover changes visually as it gets fixed. We also want the later repairs to get a little harder over time, so the game does not feel like the exact same task repeated over and over.

---

## Slide 5 - Requirement Fit and Tech Plan

Base Requirements

- Original theme: rover repair bay
- Two custom Blender assets: power module and repair tool
- Two meaningful VR interactions: insertion and repair

Advanced Features

- Physics
- Multiple object types / tools

Tools

- Blender, Three.js + WebXR, GLTFLoader, Cannon-ES
- Backup option: procedural environment assets if needed

> For the assignment requirements, this project gives us an original theme, two custom Blender assets, and two meaningful VR interactions. For the advanced features, we are planning physics and different object or tool behaviors. The main tools we are using are Blender, Three.js, WebXR, GLTFLoader, and Cannon-ES.

---

## Slide 6 - Plan, Roles, and Timeline

Main Components

- Blender modeling and export
- WebXR interaction logic for grabbing, insertion, and repair
- Rover feedback, physics, and testing

Team Roles

- Chirag: Bay layout, custom models, exports, and slide prep
- Dhrumil: WebXR scene setup, grabbing, insertion, repair logic, and physics

Timeline

- By April 20: Lock the layout, finish the first custom asset, and get the main interaction loop working
- Before the final presentation: Complete both interactions, improve feedback, test in the emulator, and clean up the experience

> For the work split, Chirag is mainly handling the bay layout, the custom models, and the exports, while Dhrumil is mainly handling the WebXR setup, grabbing, repair logic, and physics. By April 20, we want the layout locked, the first custom asset finished, and the main interaction loop working. After that, we can spend the rest of the time testing in the emulator and cleaning things up before the final presentation.
