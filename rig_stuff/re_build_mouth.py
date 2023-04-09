import maya.cmds as cmds


# TODO: function to initializes locators, user manually places them then runs the following function

def make_lip_joints(spans=1,name="", surface="my_surfaceShape", z_padding=True):

    for i in range(1, spans+1):
        if z_padding is False:
            z_padded = ""
        else:
            z_padded = f"_{str(i).rjust(2, '0')}"

        pma_add = cmds.createNode('plusMinusAverage', name=f"{name}_pma_add{z_padded}")
        pos_info = cmds.createNode('pointOnSurfaceInfo', name=f"{name}_vectorProduct{z_padded}")
        cmds.connectAttr(f"{pma_add}.output2Dx", f"{pos_info}.parameterU")
        cmds.connectAttr(f"{pma_add}.output2Dy", f"{pos_info}.parameterV")

        fbf_matrix = cmds.createNode('fourByFourMatrix', name=f"{name}_fourByFourMatrix{z_padded}")
        cmds.connectAttr(f"{pos_info}.positionX", f"{fbf_matrix}.in30")
        cmds.connectAttr(f"{pos_info}.positionY", f"{fbf_matrix}.in31")
        cmds.connectAttr(f"{pos_info}.positionZ", f"{fbf_matrix}.in32")

        # Normalized Tangent U Corresponds to X-axis
        cmds.connectAttr(f"{pos_info}.normalizedTangentUX", f"{fbf_matrix}.in00")
        cmds.connectAttr(f"{pos_info}.normalizedTangentUY", f"{fbf_matrix}.in01")
        cmds.connectAttr(f"{pos_info}.normalizedTangentUZ", f"{fbf_matrix}.in02")

        # Normalized Tangent V Corresponds to Y-axis
        cmds.connectAttr(f"{pos_info}.normalizedTangentVX", f"{fbf_matrix}.in10")
        cmds.connectAttr(f"{pos_info}.normalizedTangentVY", f"{fbf_matrix}.in11")
        cmds.connectAttr(f"{pos_info}.normalizedTangentVZ", f"{fbf_matrix}.in12")

        # Normalized Normal corresponds to Z-axis
        cmds.connectAttr(f"{pos_info}.normalizedNormalX", f"{fbf_matrix}.in20")
        cmds.connectAttr(f"{pos_info}.normalizedNormalY", f"{fbf_matrix}.in21")
        cmds.connectAttr(f"{pos_info}.normalizedNormalZ", f"{fbf_matrix}.in22")

        decomp_matrx = cmds.createNode('decomposeMatrix', name=f"{name}_decomposeMatrix{z_padded}")
        cmds.connectAttr(f"{fbf_matrix}.output", f"{decomp_matrx}.inputMatrix")

        pma_sub_default = cmds.createNode('plusMinusAverage', name=f"{name}_pma_sub{z_padded}")
        cmds.setAttr(f"{pma_sub_default}.operation", 2) #subract to default position
        cmds.connectAttr(f"{decomp_matrx}.outputTranslate", f"{pma_sub_default}.input3D[0]")

        add_rotation = cmds.createNode('animBlendNodeAdditiveRotation', name=f"{name}_add_rotation{z_padded}")
        cmds.connectAttr(f"{decomp_matrx}.outputRotateX", f"{add_rotation}.inputAX")

        jaw_jnt = cmds.joint(name=f"{name}_jaw_jnt{z_padded}", radius=0.5)
        lip_jnt = cmds.joint(name=f"{name}_jnt{z_padded}", radius=0.25)
        cmds.connectAttr(f"{pma_sub_default}.output3D", f"{lip_jnt}.translate")
        cmds.connectAttr(f"{add_rotation}.outputX", f"{lip_jnt}.rotateX")
        cmds.connectAttr(f"{decomp_matrx}.outputRotateY", f"{lip_jnt}.rotateY")
        cmds.connectAttr(f"{decomp_matrx}.outputRotateZ", f"{lip_jnt}.rotateZ")

make_lip_joints(name="lip_Rt_corner_07", z_padding=False)

make_lip_joints(spans=6, name="upp_lip_Rt")
make_lip_joints(name="upp_lip_mid_00", z_padding=False)
make_lip_joints(spans=6, name="upp_lip_Lf")

make_lip_joints(name="lip_Lf_corner_07", z_padding=False)

make_lip_joints(spans=6, name="low_lip_Rt")
make_lip_joints(name="low_lip_mid_00", z_padding=False)
make_lip_joints(spans=6, name="low_lip_Lf")

# TODO: constrain lip joints to the jaw, set up guide node. Then delete locators


#for joint in cmds.ls(selection=True):
    #cmds.parentConstraint('low_jnt', 'jaw_jnt', joint, maintainOffset=True)

