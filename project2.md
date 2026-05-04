# Project 2: Building an Interactive VR Experience

## Contents

1. [Project Requirements](#1-project-requirements)
2. [Timeline and Deliverables](#2-timeline-and-deliverables)
3. [Tips and Resources](#3-tips-and-resources)

In this project, you will integrate the tools and techniques you have learned throughout the lectures and labs/homeworks into a single, creative, and cohesive VR experience. You will work in a group of 2 to 3 students to design and implement an interactive VR scene using Blender for modeling and Three.js with WebXR for rendering and interaction in the browser.

---

## 1. Project Requirements

### 1.1 Group Size and Individual Contribution Policy

- Each group can have 2 to 3 students.
- 3-person groups must implement at least 1 additional Advanced Feature in Category A compared to 2-person groups.
- Every member must lead specific components of the project. This information must be included in both the proposal stage and the final presentation/report stage.

### 1.2 Base Requirements

All groups must implement the following features:

| Feature           | Requirement                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Theme             | A theme that goes beyond the lab/homework examples. The scene should not look like a copy of a lab or homework.                                                                                                                                                                                                                                                                                          |
| Custom 3D Assets  | At least two custom 3D models created in Blender (Labs 1-3 / Homework 1-2) and loaded via `GLTFLoader`. Each model should involve meaningful modeling work (for example, a desk lamp with a shade or a vending machine with buttons). A single primitive like a cube or cylinder does not count. You may use additional models from the web to fill the scene, but they do not count toward the minimum. |
| Core Interactions | At least two meaningful VR interactions that directly manipulate scene objects or change the environment through XR input, e.g., dragging, spawning, throwing, selecting, or collecting objects.                                                                                                                                                                                                         |

These three items are the base requirements for every group. They do not count toward the advanced feature minimums below.

### 1.3 Advanced Features

Advanced features are divided into two categories, A and B. Each feature must be distinct and functional.

A 3-person group must implement at least 1 additional Advanced Feature in Category A compared to a 2-person group.

#### 2-Person Group Minimums

| Course          | Minimum # of Advanced Features | Category A Requirement     |
| --------------- | ------------------------------ | -------------------------- |
| 376 (Undergrad) | At least 2 features            | At least 1 from Category A |
| 571 (Graduate)  | At least 3 features            | At least 2 from Category A |

#### 3-Person Group Minimums

| Course          | Minimum # of Advanced Features | Category A Requirement     |
| --------------- | ------------------------------ | -------------------------- |
| 376 (Undergrad) | At least 3 features            | At least 2 from Category A |
| 571 (Graduate)  | At least 4 features            | At least 3 from Category A |

### 1.3.1 Category A: Interaction and System Features

| Feature                             | Source                   | Requirement                                                                                                                                                                                                                             |
| ----------------------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Physics                             | Lab 7 / HW 4             | Use Cannon-ES to add physics to the scene.                                                                                                                                                                                              |
| Multiple Object Types / Modes       | Labs 1-3, 8 / HW 1, 2, 4 | Include multiple different objects, tools, or interaction modes. These should represent meaningfully different objects and must support interaction. Simple variations such as recolors or static, non-interactive models do not count. |
| Navigation / Locomotion             | New / Resources          | Add teleportation or another appropriate navigation approach if your experience benefits from it.                                                                                                                                       |
| Procedural Generation               | Lab 2 / HW 1             | Use Python / Blender scripting to generate meaningful scene content.                                                                                                                                                                    |
| Custom Interaction / System Feature | -                        | Another interaction or system feature of similar scope.                                                                                                                                                                                 |

### 1.3.2 Category B: Environment Features

| Feature                    | Source       | Requirement                                                                                                                 |
| -------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| 360-Degree Environment     | Lab 5 / HW 3 | Use a 360-degree image or video as part of the environment.                                                                 |
| Gaussian Splat Scene       | Lab 6 / HW 3 | Use a Gaussian splat scene or object together with traditional mesh objects. You do not need to train your own splat model. |
| Custom Environment Feature | -            | Another environment or presentation feature of similar scope.                                                               |

### 1.4 Additional Requirements for Graduate Students (571) Only

We summarize the additional requirements for 571 students below:

1. For a 2-person group, implement 3 advanced features (instead of 2), with at least 2 from Category A. For a 3-person group, implement 4 advanced features (instead of 3), with at least 3 from Category A.
2. The final report must follow the [IEEE Conference format](https://www.ieee.org/conferences/publishing/templates.html).

---

## 2. Timeline and Deliverables

### 2.1 Grading Summary

This project is divided into 5 parts and milestones, as summarized in the table below:

| Component                                                      |      Points | Due                             |
| -------------------------------------------------------------- | ----------: | ------------------------------- |
| Part 0: Project Signup                                         |      10 pts | April 1 by 11:59pm              |
| Part 1: Proposal Presentation                                  |      30 pts | April 13 and April 15 by 3:50pm |
| Part 2: Written Proposal                                       |      30 pts | April 20 by 11:59pm             |
| Part 3: Final Project Presentation                             |      40 pts | April 29 and May 4 by 3:50pm    |
| Part 4: Final Project Report, Demo Video, and Source Materials |      90 pts | May 4 by 11:59pm                |
| **Total**                                                      | **200 pts** |                                 |

#### 2.1.1 Late Policy

- No late submissions are accepted for presentations. You must present during your scheduled time.
- Written deliverables are accepted up to 48 hours late with a 10% per day late penalty.

### 2.2 Part 0: Project Signup (10 pts)

Form a group of 2 to 3 students and submit your group members information on Canvas by the deadline.

### 2.3 Part 1: Proposal Presentation (30 pts)

Each group will give a 5-minute presentation pitching their proposed VR experiences. Information on which group presents on which day will be released after the project signup.

- **Introduction:** Briefly introduce the VR experience and explain why VR is a good fit for this experience.
- **Environment and Interactions:** Show what will be in the scene and how the user will interact with it. A sketch, mockup, or other visualization will be helpful.
- **Plan:** Explain the main project components, who will work on each component, and your estimated timeline.

Every group member must speak during the presentation. The group will receive one presentation score, but any absent group member will receive 0 points.

Submit the proposal slides as `.pptx` or a link to Google Slides to Canvas before the start of class on the scheduled presentation date.

### 2.4 Part 2: Written Proposal (30 pts)

Your written proposal should be 1 to 2 pages long and include the following:

1. **Cover Page:** Group members and name of the project.
2. **Introduction:** Briefly introduce the VR experience. What is it about, and why does VR help this experience?
3. **Environment Design:** Describe the scene or environment you plan to build. Include a rough sketch, mockup, Blender screenshot, or simple diagram if possible.
4. **Interactions and Features:** Describe how the user will interact with the experience. Include a Feature Mapping Table that lists your planned Base Requirements and Advanced Features, categorizing them (A or B) and briefly describing how you will implement them.
5. **Task Division:** Explain who will work on which component, what you plan to build yourselves versus what you may use from external assets.
6. **Progress So Far:** Describe what has already been completed so far, e.g., models built, interactions created.

Submit the written proposal (`project2_proposal_[GroupID].pdf`) to Canvas by **April 20 at 11:59pm**.

### 2.5 Part 3: Final Project Presentation (40 pts)

Each group will give a 7-minute presentation demonstrating their completed VR experience. Information on which group presents on which day will be released after the project signup.

- **Demo:** Show your VR experience, either live in the emulator/headset or with a screen recording.
- **Design Walkthrough:** Explain your design decisions, the main components, and how they work together.
- **Individual Contributions:** Each member explains what they built.
- **Reflection:** What was the most challenging part? What would you add with more time? What did VR add that a more traditional version would not?

Every group member must speak during the presentation. The group will receive one presentation score, but any absent group member will receive 0 points.

Submit the final presentation slides as `.pptx` or a link to Google Slides to Canvas before the start of class (**3:50pm**) on the scheduled presentation date.

### 2.6 Part 4: Final Project Report (90 pts)

Your report must include the following sections:

1. **Project Overview:** What you built, the theme, and which advanced features you implemented.
2. **Scene and Interaction Description:** Describe the virtual environment and how the user navigates and interacts with it. You must provide a link to a short screen recording (~1-2 min) of the VR experience (e.g., hosted on YouTube or Google Drive). Also include at least 2-3 screenshots of the VR experience.
3. **Features Table:** Include a table that lists the base and advanced feature requirements, how these requirements are met, and the section in the report where they are discussed.
4. **Challenges and Solutions:** What challenges you encountered during development and how you addressed them. Be specific.
5. **Discussion and Future Work:** What works well in your project? What are its limitations? What would you add or improve if you had more time?
6. **Individual Contribution Table:** List each project component, who led it, and approximate contribution percentages. Vague statements such as “both members worked on everything together” are not acceptable. Even if you collaborated closely, still identify who took the lead on each component.
7. **Asset Credits (if applicable):** List any third-party models, images, videos, splat scenes, or code snippets you used, along with their source URLs. This may be a short appendix or reference list.
8. **Code and Execution Instructions:** Provide clear instructions on how to run your project. For example, specify which `.html` file should be opened (e.g., using the VS Code Live Server extension) and any other steps required to view the experience correctly in the browser.

**Format Requirements:**

- **376 (Undergrad):** Your final report should be 2 to 3 pages long. We recommend that you use the IEEE conference-style format, but it is not required.
- **571 (Graduate):** Your final report must be formatted as a 4-page IEEE conference-style paper using the [IEEE Conference Template](https://www.ieee.org/conferences/publishing/templates.html).

Submit the following to Canvas by **May 4 at 11:59pm**:

1. **Final Project Report:** A `.pdf` file (`project2_report_[GroupID].pdf`) containing the report, screenshots, link to your demo video, and instructions on how to run your project.
2. **Source Materials and Code** (`project2_source_[GroupID].zip`):
   - All original Blender files (`.blend`) created by your group.
   - All source code for your WebXR implementation (e.g., `.html`, `.js` files needed to run your project).
   - All assets (textures, models, `.glb` files, `.splat` files, etc.) necessary to run your project.

---

## 3. Tips and Resources

This project builds on content from Labs 1-8 / Homework 1-4. Here is a recap of what you have learned:

| Lab/HW       | Content                    | Summary                                                                                                                                                                           |
| ------------ | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lab 1 (HW 1) | 3D Modeling                | Blender interface, navigation, object manipulation (move, rotate, scale), and mesh editing (Extrude, Loop Cut, Bevel) to model simple furniture and props.                        |
| Lab 2 (HW 1) | Procedural Scene Building  | Use Python (`bpy`) to programmatically create scenes with walls, floors, furniture, materials, and object parenting.                                                              |
| Lab 3 (HW 2) | Texture Baking, GLB Export | Join meshes, UV unwrap, bake lighting and shadows into textures, convert materials for real-time display, and export to `.glb`.                                                   |
| Lab 4 (HW 2) | Raycasting, Point Clouds   | Simulate depth cameras, cast rays to detect surface intersections, and generate and fused point clouds.                                                                           |
| Lab 5 (HW 3) | 360-Degree Images/Videos   | Map equirectangular and cubemap content onto 3D geometry using texture coordinates. Set up WebXR viewing for immersive panoramas.                                                 |
| Lab 6 (HW 3) | 3D Gaussian Splatting      | Render Gaussian splat scenes in different modes (Splat, Ellipsoid, Point) and integrate traditional mesh objects into a splat environment.                                        |
| Lab 7 (HW 4) | Physics, Loading 3D Assets | Synchronize Three.js visuals with Cannon-ES physics bodies. Load `.glb` models via `GLTFLoader`.                                                                                  |
| Lab 8 (HW 4) | WebXR Spawn and Drag       | Handle VR controller events (`selectstart`, `selectend`, `squeezestart`), use raycasting to spawn objects at floor intersections, and attach/detach objects for drag interaction. |

### 3.1 Example Project Ideas

The following are some example project ideas. You are free to use one of these as a starting point or come up with your own.

#### 3.1.1 VR Interior Design

Start with an empty room. Spawn furniture (sofas, tables, lamps) and drag them to arrange the space. Add physics so objects fall realistically when dropped.

#### 3.1.2 Blending Real and Virtual Worlds

Use a Gaussian splat capture of a real location as the environment. Add interactive mesh objects (e.g., virtual furniture in a real room). Use invisible proxy geometry (simple boxes or planes aligned with real surfaces like floors, tables, walls) to enable physics within the splat scene.

#### 3.1.3 VR Maze Explorer

Use a Python script to randomly generate a maze layout in Blender and export it as `.glb`. Load the maze into your WebXR scene. Use teleportation to navigate the corridors. Place collectibles inside the maze that users can pick up. Every time you run the Python script, a new maze is generated. You can learn about the [maze generation algorithms here](https://en.wikipedia.org/wiki/Maze_generation_algorithm).

### 3.2 Tips

- A small, polished experience is better than a large, unfinished one.
- You can use free assets from [Sketchfab](https://sketchfab.com/features/free-3d-models), [Adobe Stock](https://ithelp.rutgers.edu/sp?id=kb_article&sysparm_article=KB0012748), [Poly Pizza](https://poly.pizza/), or [Kenney](https://kenney.nl/assets) for models beyond your required custom ones. Download them in `.glb` format and load them with `GLTFLoader`.
- Bake your Blender models before exporting to `.glb` for better visual quality.
- Test early and often in the Immersive Web Emulator.
- If your scene is small, keep the user mostly stationary. Only add locomotion when your design really benefits from it.
- If you use 360-degree images or Gaussian splats, remember that they are visual content, not collision geometry. Add floor planes or other proxy geometry if your interactions or physics need solid surfaces.
- If you need WASD keyboard controls for testing, check out [`iwer`](https://github.com/meta-quest/immersive-web-emulation-runtime) (Immersive Web Emulation Runtime), which is also used in [Meta’s WebXR First Steps](https://github.com/meta-quest/webxr-first-steps).

### 3.3 Resources

#### 3.3.1 Documentation

- [Blender API Documentation](https://docs.blender.org/api/4.5/)
- [Three.js Documentation](https://threejs.org/docs/)
- [Three.js WebXR Examples](https://threejs.org/examples/?q=webxr)
- [WebXR Device API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API)
- [Immersive Web Emulator](https://github.com/meta-quest/immersive-web-emulator)
- [Cannon-ES Documentation](https://pmndrs.github.io/cannon-es/docs/)
- [Three.js `GLTFLoader` Documentation](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)

#### 3.3.2 Free 3D Assets

- [Sketchfab](https://sketchfab.com/features/free-3d-models)
- [Adobe Stock](https://stock.adobe.com/) (Free for Rutgers Students via the IT portal: [Rutgers IT Help - What is included with Adobe Stock?](https://ithelp.rutgers.edu/sp?id=kb_article&sysparm_article=KB0012748))
- [Poly Pizza](https://poly.pizza/)
- [Kenney](https://kenney.nl/assets)

#### 3.3.3 3D Gaussian Splat Assets

- [GaussianSplats3D Demo Scene Data](https://projects.markkellogg.org/downloads/gaussian_splat_data.zip)
  - [3D Gaussian Splatting with Three.js Demo Scene](https://projects.markkellogg.org/threejs/demo_gaussian_splats_3d.php)
  - [GaussianSplats3D GitHub Repository](https://github.com/mkkellogg/GaussianSplats3D)
- [Polycam Gaussian Splatting](https://poly.cam/tools/gaussian-splatting)
- [SceneSplat-49K Dataset](https://scenesplatpp.gaussianworld.ai/)

#### 3.3.4 Useful Tutorials

Below is a list of useful tutorials that may help you with your project:

- Teleportation example: [Three.js `webxr_vr_teleport`](https://github.com/mrdoob/three.js/blob/dev/examples/webxr_vr_teleport.html)
- Other Three.js WebXR examples: [Three.js WebXR Examples Page](https://threejs.org/examples/?q=webxr)
- Maze generation: [Maze Generation Algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- Meta tutorial: [Meta’s WebXR First Steps](https://developers.meta.com/horizon/documentation/web/webxr-first-steps/)

---

**Source:** `project2.pdf`
