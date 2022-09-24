'''
Zeroes out selected controllers keyable attributes, if they are in the defined controller set...
'''

import maya.cmds as cmds

# First define the set with the character's controls
ctrls_list = cmds.listConnections("Controls_Set" + '.dagSetMembers')
# Get what is selected, only if visible
selection = cmds.ls(sl=True, v=True)

# If selection items ARE in the controls set, zero the keyable attributes
if not set(selection).isdisjoint(set(ctrls_list)):
    for obj in selection:
        keyable = cmds.listAttr(obj, keyable=1, unlocked=1, settable=1)
        for attr in keyable:
            default = cmds.attributeQuery(attr, node=obj, listDefault=1)
            if cmds.getAttr(obj + "." + attr, settable=1) != 0:
                cmds.setAttr(obj + "." + attr, default[0])

        print (f"{obj} has been zeroed out!")
else:
    cmds.warning("Sorry! Make sure your selection is only visible controllers.")