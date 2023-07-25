import maya.cmds as cmds


def get_jnt_children(j):
    children = cmds.listRelatives(j, c=True, type="joint") or []
    return children


def get_jnt_heirarchy(j):
    cmds.select(cl=True)
    cmds.select(j, toggle=True)
    joints = [j] + cmds.listRelatives(allDescendents=True, type='joint')
    cmds.select(cl=True)
    joints.sort()
    return joints


def clear_orients(j):
    cmds.setAttr(f"{j}.jointOrientX", 0)
    cmds.setAttr(f"{j}.jointOrientY", 0)
    cmds.setAttr(f"{j}.jointOrientZ", 0)


def jnt_chain_pos(j):
    pos = [cmds.xform(j, q=True, t=True, ws=True)]
    children = get_jnt_children(j)
    for child in children:
        pos.extend(jnt_chain_pos(child))
    return pos


def crv_to_clusters(crv="", exclude=None):
    clusters = []
    cvs = cmds.ls(f'{crv}.cv[:]', fl=True)  # Get all CVs from curve

    if exclude:  # CVs you want to ignore
        if isinstance(exclude, str):
            center_cvs = [cv for cv in cvs if cmds.getAttr(cv)[0][0] == 0.0]
            center_cvs_z = [cmds.getAttr(cv)[0][2] for cv in center_cvs]

            if exclude == "front" or exclude == "back":
                if exclude == "front":
                    cvs.remove(center_cvs[center_cvs_z.index(max(center_cvs_z))])  # Excluding front CV

                elif exclude == "back":
                    cvs.remove(center_cvs[center_cvs_z.index(min(center_cvs_z))])  # Excluding back CV

                else:
                    raise ValueError('Invalid string. Enter either \"front\" or  \"back\" to exclude')
        elif isinstance(exclude, list):
            for e in exclude:
                cvs.remove(cvs[e])
        elif isinstance(exclude, int):
            cvs.remove(exclude)
        else:
            raise ValueError('Use str \"front\", \"back\", or list of CVs as ints, or single cv as an int')

    if cvs:  # Check if we found any cvs
        padding = len(str(cvs.index(cvs[-1])))
        for cv in cvs:
            z_padded = f"{str(cvs.index(cv)).rjust(padding, '0')}"
            n = f"{str(crv.partition('_')[0])}_cluster_{z_padded}"
            clust = cmds.cluster(cv, name=f"{n}")  # Create cluster on a cv
            grp = cmds.group(em=True, name=f"{n}_grp")
            cmds.matchTransform(grp, clust)
            cmds.parent(clust, grp)
            clusters.append(grp)
        grp = cmds.group(em=True, name=f"{crv.partition('_')[0]}_cluster_grp")
        cmds.parent(clusters, grp)
        clusters.sort()
    else:
        cmds.warning('Found no CVs!')
    return clusters


def crv_collide_with_geo(clusters, collider=""):
    cmds.select(collider, r=True)
    import maya.mel as mel
    mel.eval("cMuscle_makeMuscle(0);")
    cmds.select(clusters, r=True)
    mel.eval("cMuscle_rigKeepOutSel()")
    for c in clusters:
        name = c.split("_")
        name = f"{name[0]}_{name[1]}_{name[2]}_keepOut"
        keep_out = cmds.listRelatives(c)
        keep_out = cmds.rename(keep_out, f"{name}")
        cmds.rename(cmds.listRelatives(keep_out)[1], f"{name}Driven")
        keep_out_shape = cmds.listRelatives(keep_out)[0]

        cmds.setAttr(f"{keep_out_shape}.inDirectionY", -0.5)
        if cmds.getAttr(f"{c}.translateX") < 0:
            cmds.setAttr(f"{keep_out_shape}.inDirectionX", -1)
        elif cmds.getAttr(f"{c}.translateX") > 0:
            cmds.setAttr(f"{keep_out_shape}.inDirectionX", 1)
        else:
            cmds.setAttr(f"{keep_out_shape}.inDirectionX", 0)
            cmds.setAttr(f"{keep_out_shape}.inDirectionZ", -1)

    cmds.select(collider, add=True)
    mel.eval("cMuscle_keepOutAddRemMuscle(1);")
    cmds.select(cl=True)


def crv_cluster_collusion(crv, collider, exclude=None, jnt=True):
    clusters = crv_to_clusters(crv=crv, exclude=exclude)
    crv_collide_with_geo(clusters=clusters, collider=collider)

    if jnt:
        name = crv.partition("_")[0]
        offsets = []
        for index, c in enumerate(clusters):
            padding = len(str(clusters.index(clusters[-1])))
            z_padded = f"{str(index).rjust(padding, '0')}"

            joint = cmds.joint(name=f"{name}_{z_padded}")
            loc = cmds.createNode("locator", name=f"{joint}_locShape")
            loc = cmds.rename(cmds.listRelatives(loc, p=True)[0], f"{joint}_loc")
            cmds.parent(joint, loc)
            offset = cmds.group(loc, name=f"{joint}_offset")
            offsets.append(offset)

            poc_info = f"{joint}_pointOnCurveInfo"
            cmds.createNode('pointOnCurveInfo', name=poc_info)
            cmds.connectAttr(f"{crv}.local", f"{poc_info}.inputCurve")

            parameter = float(index) / float(len(clusters))
            cmds.setAttr(f"{poc_info}.parameter", parameter)
            cmds.setAttr(f"{poc_info}.turnOnPercentage", 1)
            cmds.connectAttr(f"{poc_info}.position", f"{offset}.translate")

        grp = cmds.group(em=True, name=f"{name}_grp")
        cmds.parent(offsets, grp)
        return offsets
    # TODO:
    #   Cleanup, DNT group check,
    #   make clone of joints for skin,
    #   make non-skin joints invisible and non editable
    #   Fancier controls for tweaking
    #   option for symmetry to name L, R, and C joints


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
        cmds.rebuildCurve(crv, rt=0, s=len(get_jnt_heirarchy(j)) - 1, kr=0, ch=0)  # Smooth curve - optional
    return shape


def jnt_chain_distr_on_crv(j="", crv="", rebuild_chain=False):
    # TODO figure out way to make joints more equidistant from each other

    """
    Attempts to evenly distribute joints along an existing curve
    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the curve
        crv: the curve to distribute existing joints along
        rebuild_chain: if True, re-parents the joints chain after distribution along the curve in world space

    Returns:
        None
    """
    joints = get_jnt_heirarchy(j)
    crv = crv

    for index, joint in enumerate(joints):
        if index != 0:
            cmds.setAttr(f"{joint}.translateY", 0)
            cmds.setAttr(f"{joint}.translateZ", 0)
            clear_orients(joint)

    for joint in joints:
        try:
            cmds.parent(joint, world=True)
        except:
            clear_orients(joint)
        clear_orients(joint)

    for index, joint in enumerate(joints):
        poc_info = f"{joint}_pointOnCurveInfo"
        cmds.createNode('pointOnCurveInfo', name=poc_info)
        cmds.connectAttr(f"{crv}.local", f"{poc_info}.inputCurve")

        parameter = float(index) / float(len(joints) - 1)
        cmds.setAttr(f"{poc_info}.parameter", parameter)
        cmds.setAttr(f"{poc_info}.turnOnPercentage", 1)
        cmds.connectAttr(f"{poc_info}.position", f"{joint}.translate")

    if rebuild_chain is True:
        for joint in joints:
            poc_info = f"{joint}_pointOnCurveInfo"
            cmds.disconnectAttr(f"{poc_info}.position", f"{joint}.translate")
            cmds.delete(poc_info)

        for index, joint in enumerate(joints):  # TODO: this assumes X twist axis, what if its Y or Z?
            nxt = index + 1
            world_up = cmds.group(em=True, name=f"{joint}_worldUp")
            cmds.delete(cmds.parentConstraint(joint, world_up, mo=0))
            if nxt < len(joints):
                nxt_joint = joints[nxt]
                cmds.delete(cmds.aimConstraint(nxt_joint, joint, aim=[1, 0, 0], u=[0, 0, 1], wut="objectrotation",
                                               wu=[0, 0, -1], wuo=world_up))
                cmds.makeIdentity(joint, apply=True)
                cmds.parent(nxt_joint, joint)
                if nxt == len(joints) - 1:
                    clear_orients(nxt_joint)
            cmds.delete(world_up)


def jnt_chain_to_surface(j, name="", width=4):
    """
    Creates surface that can be used for ribbon from an existing joint chain
    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the surface
        name: name of the chain
        width: the width of the surface

    Returns:
        [shape_surface, shape_curve]: [0]shape node of the nurbs surface created, and [1] the curve it came from
    """
    crv_orig = jnt_chain_to_crv(j=j, name=name, smooth=True)
    jnt_chain_distr_on_crv(j=j, crv=crv_orig, rebuild_chain=True)

    crv_a = cmds.duplicate(crv_orig)
    cmds.setAttr(f"{crv_a[0]}.translateX", width / 2)
    crv_b = cmds.duplicate(crv_orig)
    cmds.setAttr(f"{crv_b[0]}.translateX", -width / 2)

    ribbon = cmds.loft(crv_b, crv_a, ch=0, ar=1, d=3, u=1, ss=1, rsn=True, name=f'{name}_ribbon')
    shape_surface = cmds.rename(cmds.listRelatives(ribbon, c=True, shapes=True)[0], f'{name}_ribbonShape')
    cmds.rebuildSurface(shape_surface, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kc=0, su=4, du=3, tol=0.01, fr=0, dir=0)
    shape_curve = cmds.listRelatives(crv_orig, p=True)[0]

    cmds.delete(crv_a)
    cmds.delete(crv_b)

    return [shape_surface, shape_curve]


def setup_ribbon_base(j="", name="", follow_jnts=True, width=4, loc_shape=False):
    """
    Makes a ribbon from a chain of joints, and distributes transform nodes to follow the ribbon using uv pin

    Args:
        j: top joint in hierarchy. Best if its children are only the joints you want on the surface
        name: name of the chain
        follow_jnts: True if you want the groups to more closely match the source joint chain's behavior
        width: width of the resulting ribbon curve
        loc_shape: whether you want to see locator shape where the transform groups are made

    Returns:
        [grps, ribbon[0], ribbon[1]]: list of transform nodes, the ribbon's shape, and the curve the joints following
    """
    grps = []
    ribbon = jnt_chain_to_surface(j=j, name=name, width=width)
    shape = ribbon[0]
    joints = get_jnt_heirarchy(j)

    uv_pin = cmds.createNode("uvPin", name=f"{ribbon[0]}_uvPin")
    cmds.connectAttr(f"{shape}.worldSpace[0]", f"{uv_pin}.deformedGeometry")

    for index, joint in enumerate(joints):
        loc = cmds.createNode("locator", name=f"{joint}_locShape")
        loc = cmds.rename(cmds.listRelatives(loc, p=True)[0], f"{joint}_loc")
        if loc_shape is False:
            cmds.delete(f"{joint}_locShape")
        cmds.setAttr(f"{loc}.rotateY", -90)
        cmds.setAttr(f"{loc}.rotateZ", 180)

        grp = cmds.group(em=1, name=f"{joint}_grp")  # Change to Offset
        cmds.delete(cmds.parentConstraint(loc, grp, mo=0))
        cmds.parent(grp, loc)
        grps.append(grp)

        if follow_jnts:
            closest_pos = cmds.createNode("closestPointOnSurface", name=f"{joint}_closestPointOnSurface")
            cmds.connectAttr(f"{shape}.worldSpace[0]", f"{closest_pos}.inputSurface")

            decomp_matrix = cmds.createNode("decomposeMatrix", name=f"{joint}_decomposeMatrix")
            cmds.connectAttr(f"{joint}.worldMatrix[0]", f"{decomp_matrix}.inputMatrix")
            cmds.connectAttr(f"{decomp_matrix}.outputTranslate", f"{closest_pos}.inPosition")

            cmds.connectAttr(f"{closest_pos}.result.parameterU", f"{uv_pin}.coordinate[{index}].coordinateU")
            cmds.connectAttr(f"{closest_pos}.result.parameterV", f"{uv_pin}.coordinate[{index}].coordinateV")
        else:
            param_u = float(index) / float(len(joints) - 1)
            cmds.setAttr(f"{uv_pin}.coordinate[{index}].coordinateU", param_u)
            cmds.setAttr(f"{uv_pin}.coordinate[{index}].coordinateV", 0.5)

        cmds.connectAttr(f"{uv_pin}.outputMatrix[{index}]", f"{loc}.offsetParentMatrix")

    return [grps, ribbon[0], ribbon[1]]


def setup_ik_spline(jnt_a, jnt_b, name, crv):
    cmds.select(jnt_a, jnt_b, r=True, ne=True)
    ik = cmds.ikHandle(sol="ikSplineSolver", c=crv, ccv=False, roc=True, pcv=True, n=f"{name}_ikSplineHandle")
    cmds.select(cl=True)
    cmds.rename(ik[1], f"{jnt_a}_effector")
    cmds.setAttr(f"{ik[0]}.visibility", 0)
    return ik


# TODO: in future, move this to a class
def setup_rail_spine(j="", name="", neck="", stretch=True, width=4):
    """
    Sets up a rail spine as demonstrated by Perry Leijten

    https://www.perryleijten.com/en/works/railSplineRD

    Args:
        j: top spine joint in hierarchy. Best if its children are only the joints you want on the surface
        name: name of the chain
        neck: specify if there is a neck joint
        stretch: if you would like to add stretch. Currently, only game engine friendly stretch via translate
        width: width of the resulting ribbon curve

    Returns:
        None
    """
    cmds.select(cl=True)
    ribbon = setup_ribbon_base(j=j, name=name, follow_jnts=True, width=width)
    grps = ribbon[0]
    surface = ribbon[1]
    curve = ribbon[2]
    joints = get_jnt_heirarchy(j)
    start_jnt = joints[0]
    mid_jnt = joints[int((len(joints) - 1) / 2)]
    end_jnt = joints[len(joints) - 1]
    ctrls = []
    ctrl_grps = []
    rail_jnt = ""
    ik = setup_ik_spline(end_jnt, start_jnt, name, curve)[0]

    for ik_jnt in [start_jnt, mid_jnt, end_jnt]:  # 3 Joints that will tweak the spine
        clone = cmds.joint(n=f"{ik_jnt}_IK", rad=2.5)
        cmds.delete(cmds.parentConstraint(ik_jnt, clone))
        try:
            cmds.parent(clone, world=True)
            cmds.makeIdentity(clone, apply=True)
        except:
            cmds.makeIdentity(clone, apply=True)
        ctrl = cmds.circle(normal=(0, 1, 0), radius=width * 5, name=f"{clone}_ctrl")[0]
        grp = cmds.group(em=1, name=f"{clone}_grp")
        cmds.parent(ctrl, grp)
        cmds.delete(cmds.pointConstraint(clone, grp, mo=0))
        cmds.parent(clone, ctrl)
        ctrls.append(ctrl)
        ctrl_grps.append(grp)

    cmds.select(cl=True)

    for index, joint in enumerate(joints):
        cmds.setAttr(f"{joint}.drawStyle", 2)
        if joint is not end_jnt:
            rail_jnt = cmds.joint(name=f"{name}Rail_{index}")
            cmds.delete(cmds.pointConstraint(grps[index], rail_jnt, mo=0))
            cmds.delete(cmds.aimConstraint(grps[index + 1], rail_jnt, aim=[1, 0, 0], u=[0, 0, 1], wut="objectrotation",
                                           wu=[0, 0, 1], wuo=grps[index]))
            cmds.makeIdentity(rail_jnt, apply=True)
            cmds.pointConstraint(grps[index], rail_jnt, mo=0)
            cmds.aimConstraint(grps[index + 1], rail_jnt, aim=[1, 0, 0], u=[0, 0, 1], wut="objectrotation",
                               wu=[0, 0, 1], wuo=grps[index])
        else:  # End of spine connects to neck, so make it follow the orient of chest control
            rail_jnt = cmds.joint(name=f"{name}Rail_{index}")
            cmds.pointConstraint(grps[index], rail_jnt, mo=0)
            cmds.orientConstraint(f"{end_jnt}_IK", rail_jnt, mo=1)

    if stretch:
        curve_info = cmds.createNode("curveInfo", name=f"{name}_stretch_curveInfo")
        cmds.connectAttr(f"{curve}.worldSpace[0]", f"{curve_info}.inputCurve")

        multi_div = cmds.createNode("multiplyDivide", name=f"{name}_stretch_multiplyDivide")
        cmds.setAttr(f"{multi_div}.operation", 2)  # Divide
        cmds.connectAttr(f"{curve_info}.arcLength", f"{multi_div}.input1X")
        cmds.setAttr(f"{multi_div}.input2X", cmds.getAttr(f"{curve_info}.arcLength"))

        end_ctrl = ctrls[-1]
        cmds.addAttr(f"{end_ctrl}", ln="Stretch", at="float", min=0, max=1, keyable=1)
        for ctrl in ctrls[:-1]:
            cmds.addAttr(ctrl, ln="Stretch", proxy=f"{end_ctrl}.Stretch", at="float", min=0, max=1, keyable=1)

        blend = cmds.createNode("blendColors", name=f"{name}_stretch_blendColors")
        cmds.connectAttr(f"{end_ctrl}.Stretch", f"{blend}.blender")
        cmds.connectAttr(f"{multi_div}.output.outputX", f"{blend}.color1.color1R")
        cmds.connectAttr(f"{multi_div}.input2.input2Y", f"{blend}.color2.color2R")

        for joint in joints[:-1]:
            cmds.connectAttr(f"{blend}.output.outputR", f"{joint}.scale.scaleX.")

    cmds.skinCluster(f"{start_jnt}_IK", f"{mid_jnt}_IK", f"{end_jnt}_IK", f"{curve}", n=f"{curve}Shape_skinCluster")
    cmds.skinCluster(f"{start_jnt}_IK", f"{mid_jnt}_IK", f"{end_jnt}_IK", f"{surface}", n=f"{surface}_skinCluster")

    # TODO: Check if do not touch group exists by setting as parameter
    hide = cmds.group(em=True, name="DO_NOT_TOUCH", w=True)
    cmds.setAttr(f"{hide}.visibility", 0)
    for obj in [curve, cmds.listRelatives(surface, parent=True)[0], ik]:
        cmds.parent(obj, hide)
        cmds.setAttr(f"{obj}.visibility", 0)
    for g in grps:
        cmds.setAttr(f"{g}.visibility", 0)
        g = cmds.listRelatives(g, parent=True)[0]
        cmds.parent(g, hide)
        cmds.setAttr(f"{g}.visibility", 0)

    # TODO: Lock and hide attrs to finalize cleanup
    if neck != "":
        cmds.parent(neck, rail_jnt)
    grp = cmds.group(em=1, name=f"{name}Rail_grp")
    cmds.parent(f"{name}Rail_0", grp)
    cmds.parent(ctrl_grps, grp)


crv_cluster_collusion(crv="Collar_curve", collider="Neck_collusion_geo", exclude="front", jnt=True)
setup_rail_spine(j='C_Spine_0', name="C_Spine", neck="C_Neck", stretch=True, width=4)