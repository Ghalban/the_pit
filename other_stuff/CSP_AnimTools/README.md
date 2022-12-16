# What is this?
Clip Studio Paint Auto Action Set to get around CSP's jankiness when it comes to its animation tools. Inspired by OpenToonz.

# How To Install:
[Download](https://github.com/Ghalban/the_pit/blob/main/other_stuff/CSP_AnimTools/AnimTools.laf) and drag and drop AnimTools.laf to your CSP Auto Actions panel.

# New Nested Animation Folder
Creates a nested animation folder template with Three lineart layers designated to different tasks: 
1. **LN - Folder for Lineart**
		This folder is set as a *reference layer* to work with the paint bucket tool on **FILL** layer.
		**LN layers are intended to be drawn on with only Black (0,0,0) brush color.**
	| Layer Name|Type|
	|--|--|
	| LN_main | grayscale vector layer for main linework |
	| LN_a | red vector layer marks the border of special fills |
	| LN_b|blue vector layer marks the border of special fills|
	
You can do neat stuff like filter by layer type on multiple cels to, say, change the color of all red lines, change draft layer to a working layer, and so on. 

For example, here's scrub selecting in Search Layer Panel to hide multiple special fill (red) boundaries: 
![gif](https://cdn.discordapp.com/attachments/1033537066706944050/1047985440071893032/template_advantage.gif)

2. **FILL - Raster Color Layer to assist with filling linework with flat color** 
It references the contents of LN folder for fill boundaries.
**For best results:** set bucket tool with the following defaults so it fills the vector line art completely:

![enter image description here](https://i.imgur.com/Xf3NJad.png)

3. **SK -** **a Draft Vector Layer for a sketch**
Draft layers can be excluded from export and ignored by tools that refer to multiple layers.
**If you already have a sketch on a different animation folder, I recommend deleting this layer first nested cel is assigned. Its not a bad idea to keep the layers you need to meet the goal of your animation, and remove anything that will not be used from the get go to keep your file slim and easy to navigate.**

# DO NOT CHANGE THE NAMES OF ANY BASE TEMPLATE LAYERS UNDER THE ANIMATION FOLDER! 
### Most of these actions rely on exact layer names to work correctly. You can add any additional layers you need, but do not re-name the ones set by the template.

# Duplicate Nested Cel 
Duplicates a Nested Animation Cel, making it the following frame.
- ⚠️If **LN** Lineart Folder is NOT the topmost folder under the nested cel, this WILL NOT WORK!

# Duplicate Nested Cel on 3's 
Duplicates a Nested Animation Cel, shifting it forward at the third next frame
- ⚠️If **LN** Lineart Folder is NOT the topmost folder, THIS WILL NOT WORK!
- ⚠️If the start frame of the animation cel is NOT selected, THIS WILL NOT WORK!

# New Cel In Order
Makes a new animation Cel and updates the numbering of the Cels properly.

# Delete Cel AND Layer
Removes a Cel from the timeline and its corresponding Layer from the layer panel.
- ⚠️ If the nested animation folder you want to delete for good (the one with the frame number) is not selected,and layers it contains are the *Editing Target* (indicated by pencil ✏️ icon next to 👁️ visibility toggle)... THIS WILL NOT WORK!

|GOOD|BAD|
|--|--|
| ![Nice](https://i.imgur.com/VTKB4NF.png) |![BOOOO!!!](https://i.imgur.com/LssvFK6.png)  |

# (Nested Layer) as Editing Target x12
For up to 12 Cels per click, each Cel corresponding layer type is marked as the *Editing Target.*

Iterates 12 times, so may not end up in the same place Cel you started in, or even overshoot by a lot! 

Thats ok! It only marks the layers as editing target :)

 ***Maintaining the layer names is critical, or this time-saving action will not work.***
	
*This is very useful for when you want to focus on flipping through 1 layer type, such as in the sketch phase (SK), ink (LN), and paint (FILL). It saves time of manually selecting each layer as the editing target one at a time.. and works hand in hand with...*

# Combining This Action Set with a Keyboard Shortcut for selecting Next and Previous Cels
Flip forward and backward between your cels, work more effectively, more organized and get around some of CSP's quirks!
![Please Set these Keyboard Shortcuts I am Begging](https://i.imgur.com/Hc7LIzd.png)

# [🕊️ Twitter](https://twitter.com/Ghalban_)
