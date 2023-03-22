import maya.cmds as cmds


def make_eyelid_joints(spans=14, name="", parent=None):
    parent_grp = parent
    if parent is None:
        parent_grp = name[:-3].strip() + "grp"

    for i in range(1, spans):
        z_padded = str(i).rjust(2, '0')
        curve = f"{name}_curveShape"
        jnt = f"{name}_jnt_{z_padded}"
        poc_info = f"{name}_pointOnCurveInfo_{z_padded}"
        vctr_prod = f"{name}_vectorProduct_{z_padded}"
        multi_div = f"{name}_multiplyDivide_{z_padded}"

        cmds.joint(name=jnt, radius=0.25)
        cmds.parent(jnt, parent_grp)

        cmds.createNode('pointOnCurveInfo', name=poc_info)

        cmds.connectAttr(f"{curve}.local", f"{poc_info}.inputCurve")

        parameter = float(i) / float(spans)
        cmds.setAttr(f"{poc_info}.parameter", parameter)
        cmds.setAttr(f"{poc_info}.turnOnPercentage", 1)

        cmds.createNode('vectorProduct', name=vctr_prod)
        cmds.setAttr(f"{vctr_prod}.operation", 0)
        cmds.setAttr(f"{vctr_prod}.normalizeOutput", 1)

        cmds.createNode('multiplyDivide', name=multi_div)
        cmds.setAttr(f"{multi_div}.input2X", 4)
        cmds.setAttr(f"{multi_div}.input2Y", 4)
        cmds.setAttr(f"{multi_div}.input2Z", 4)

        cmds.connectAttr(f"{poc_info}.result.position", f"{vctr_prod}.input1")
        cmds.connectAttr(f"{vctr_prod}.output", f"{multi_div}.input1")
        cmds.connectAttr(f"{multi_div}.output", f"{jnt}.translate")  # Joints same distance from parent origin

        # aim at parent origin (without pointing backward relative to world)
        cmds.aimConstraint(parent_grp, jnt, mo=False, aim=[0, 0, -1], wut="objectrotation", wuo=parent_grp)


make_eyelid_joints(name="Lf_eyelid_upp")
make_eyelid_joints(name="Lf_eyelid_low")
make_eyelid_joints(name="Rt_eyelid_upp")
make_eyelid_joints(name="Rt_eyelid_low")
