import maya.cmds as cmds

def get_vtx_pos():
    """
    Gets positions of mesh's verticies the faster than loop

    Returns:
       list[tuple]: [(x, y, z), (x, y, z)...]
    """
    
    # Query world space translation of each vertex of mesh main
    vtx = cmds.xform('main.vtx[*]', q=True, ws=True, t=True)

    # Zip xyz into tuple. Not good for non-manifold geo!
    pos = zip(vtx[0::3], vtx[1::3], vtx[2::3])

    return list(pos)
  
