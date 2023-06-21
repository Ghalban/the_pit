import maya.cmds as cmds


def get_jnt_children(j):
    children = cmds.listRelatives(j, c=True, type="joint") or []
    return children


def jnt_chain_pos(j):
    pos = [cmds.xform(j, q=True, t=True, ws=True)]
    children = get_jnt_children(j)
    for child in children:
        pos.extend(jnt_chain_pos(child))
    return pos


def jnt_chain_to_crv(j="", smooth=True, name="curve"):
    """
    Create a curve from positions of joints in a joint hierarchy
    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the curve
        smooth: If True, smooths the resulting curve
        name: the name of the curve

    Returns:
        shape: shape node of the nurbsCurve
    """
    joints = jnt_chain_pos(j)
    crv = cmds.curve(n=f'{name}_curve', d=1, p=joints)
    shape = cmds.rename(cmds.listRelatives(crv, c=True, shapes=True)[0], f'{name}_curveShape')
    if smooth is True:
        cmds.rebuildCurve(crv, rt=0, s=len(get_jnt_children(j)) + 1)  # Smooth curve - optional
    return shape


def clear_orients(j):
    cmds.setAttr(f"{j}.jointOrientX", 0)
    cmds.setAttr(f"{j}.jointOrientY", 0)
    cmds.setAttr(f"{j}.jointOrientZ", 0)


def jnt_chain_distr_on_crv(j="", crv="", rebuild_chain=False):
    """
    Attempts to evenly distribute joints along an existing curve
    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the curve
        crv: the curve to distribute existing joints along
        rebuild_chain: if True, re-parents the joints chain after distribution along the curve in world space

    Returns:
        None
    """
    cmds.select(cl=True)
    cmds.select(f'{j}', toggle=True)
    joints = [j] + cmds.listRelatives(allDescendents=True, type='joint')
    joints.sort()
    crv = crv
    for i in joints:
        try:
            cmds.parent(i, world=True)
        except:
            clear_orients(i)
        clear_orients(i)

    for i in joints:
        poc_info = f"{i}_pointOnCurveInfo"
        cmds.createNode('pointOnCurveInfo', name=poc_info)
        cmds.connectAttr(f"{crv}.local", f"{poc_info}.inputCurve")

        joint_index = joints.index(i)
        parameter = float(joint_index) / float(len(joints) - 1)
        cmds.setAttr(f"{poc_info}.parameter", parameter)
        cmds.setAttr(f"{poc_info}.turnOnPercentage", 1)
        cmds.connectAttr(f"{poc_info}.position", f"{i}.translate")

    if rebuild_chain is True:
        for i in joints:
            poc_info = f"{i}_pointOnCurveInfo"
            cmds.disconnectAttr(f"{poc_info}.position", f"{i}.translate")
            cmds.delete(poc_info)

        for index, item in enumerate(joints):  # TODO: this assumes X down the bone, what if its Y or Z?
            nxt = index + 1
            if nxt < len(joints):
                nxt_item = joints[nxt]
                if nxt == len(joints) - 1:
                    cmds.delete(cmds.aimConstraint(nxt_item, item, aim=[1, 0, 0], u=[0, 0, -1]))
                else:
                    cmds.delete(cmds.aimConstraint(nxt_item, item, aim=[1, 0, 0], u=[0, 0, 1]))
                cmds.makeIdentity(item, apply=True)
                cmds.parent(nxt_item, item)
                if nxt == len(joints) - 1:
                    clear_orients(nxt_item)


def jnt_chain_to_surface(j, name="", width=4.0):
    """
    Creates surface that can be used for ribbon from an existing joint chain
    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the surface
        name: name of the chain
        width: the width of the surface

    Returns:
        shape: shape node of the nurbs surface created
    """
    crv_orig = jnt_chain_to_crv(j=j, name=name, smooth=True)
    jnt_chain_distr_on_crv(j=jnt, crv=crv_orig, rebuild_chain=True)
    cmds.delete(cmds.listRelatives(crv_orig, parent=True))

    crv_orig = jnt_chain_to_crv(j=j, name=name, smooth=False)  # Aligned on smoothed, distributed chain
    crv_a = cmds.duplicate(crv_orig)
    cmds.setAttr(f"{crv_a[0]}.translateX", width / 2)
    crv_b = cmds.duplicate(crv_orig)
    cmds.setAttr(f"{crv_b[0]}.translateX", -width / 2)

    ribbon = cmds.loft(crv_b, crv_a, ch=True, ar=1, d=3, u=1, ss=1, rsn=True, name=f'{name}_surface')
    shape = cmds.rename(cmds.listRelatives(ribbon, c=True, shapes=True)[0], f'{name}_surfaceShape')

    cmds.delete(crv_a)
    cmds.delete(crv_b)

    return shape

# TODO: ribbon setup with uvpin, rail setup, UI


jnt = 'C_Spine_0'
# curve = jnt_chain_to_crv(j=jnt, name="C_Spine")
# jnt_chain_distr_on_crv(j=jnt, crv=curve, rebuild_chain=True)
jnt_chain_to_surface(j=jnt, name="C_Spine", width=4.0)
