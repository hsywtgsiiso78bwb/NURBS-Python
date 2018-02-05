"""
.. module:: exchange_helpers
    :platform: Unix, Windows
    :synopsis: CAD exchange and interoperability module for NURBS-Python

.. moduleauthor:: Onur Rauf Bingol <orbingol@gmail.com>

"""

import warnings

from . import BSpline, NURBS
from . import Multi
from . import exchange_helpers as exh


def save_obj(surf_in=None, file_name=None, vertex_spacing=2):
    """ Saves surfaces as a .obj file.

    This function serves as a router between :py:func:`save_obj_single` and :py:func:`save_obj_multi`.

    :param surf_in: surface or surfaces to be saved
    :type surf_in: BSpline.Surface, NURBS.Surface or Multi.MultiAbstract
    :param file_name: name of the output file
    :type file_name: str
    :param vertex_spacing: size of the triangle edge in terms of points sampled on the surface
    :type vertex_spacing: int
    """
    if isinstance(surf_in, Multi.MultiAbstract):
        save_obj_multi(surf_in, file_name, vertex_spacing)
    else:
        save_obj_single(surf_in, file_name, vertex_spacing)


# Saves B-Spline and/or NURBS surface as a Wavefront OBJ file
def save_obj_single(surface=None, file_name=None, vertex_spacing=2):
    """ Saves a single surface as a .obj file.

    :param surface: surface to be saved
    :type surface: BSpline.Surface, NURBS.Surface
    :param file_name: name of the output file
    :type file_name: str
    :param vertex_spacing: size of the triangle edge in terms of points sampled on the surface
    :type vertex_spacing: int
    """
    # Input validity checking
    if not isinstance(surface, (BSpline.Surface, NURBS.Surface)):
        raise ValueError("Input is not a surface")
    if not file_name:
        raise ValueError("File name field is required")
    if vertex_spacing < 1 or not isinstance(vertex_spacing, int):
        raise ValueError("Vertex spacing must be an integer value and it must be bigger than zero")

    # Create the file and start saving triangulated surface points
    try:
        with open(file_name, 'w') as fp:
            fp.write("# Generated by NURBS-Python\n")
            vertices, triangles = exh.make_obj_triangles(surface.surfpts,
                                                         int((1.0 / surface.delta) + 1), int((1.0 / surface.delta) + 1),
                                                         vertex_spacing)

            # # Evaluate face normals
            # uv_list = exh.make_obj_face_normals_uv(surface.delta, vertex_spacing)

            # Write vertices
            for vert_row in vertices:
                for vert in vert_row:
                    line = "v " + str(vert.x) + " " + str(vert.y) + " " + str(vert.z) + "\n"
                    fp.write(line)

            # Write vertex normals
            for vert_row in vertices:
                for vert in vert_row:
                    sn = surface.normal(vert.uv[0], vert.uv[1], True)
                    line = "vn " + str(sn[1][0]) + " " + str(sn[1][1]) + " " + str(sn[1][2]) + "\n"
                    fp.write(line)

            # Write faces
            for t in triangles:
                vl = t.vertex_ids
                line = "f " + str(vl[0]) + " " + str(vl[1]) + " " + str(vl[2]) + "\n"
                fp.write(line)
    except IOError:
        print("Cannot open " + str(file_name) + " for writing")


# Saves B-Spline and/or NURBS surfaces as a single Wavefront OBJ file
def save_obj_multi(surface_list=(), file_name=None, vertex_spacing=2):
    """ Saves multiple surfaces as a single .obj file.

    :param surface_list: list of surfaces to be saved
    :type surface_list: list
    :param file_name: name of the output file
    :type file_name: str
    :param vertex_spacing: size of the triangle edge in terms of points sampled on the surface
    :type vertex_spacing: int
    """
    # Input validity checking
    if not isinstance(surface_list, Multi.MultiAbstract):
        raise ValueError("Input must be a list of surfaces")
    if not file_name:
        raise ValueError("File name field is required")
    if vertex_spacing < 1 or not isinstance(vertex_spacing, int):
        raise ValueError("Vertex spacing must be an integer value and it must be bigger than zero")

    # Create the file and start saving triangulated surface points
    try:
        with open(file_name, 'w') as fp:
            fp.write("# Generated by NURBS-Python\n")
            vertex_offset = 0  # count the vertices to update the face numbers correctly

            # Initialize lists for vertices, vertex normals and faces
            str_v = []
            str_vn = []
            str_f = []

            # Loop through MultiSurface object
            for surface in surface_list:
                if not isinstance(surface, (BSpline.Surface, NURBS.Surface)):
                    warnings.warn("Encountered a non-surface object")

                # Set surface delta
                surface.delta = surface_list.delta

                # Generate triangles
                vertices, triangles = exh.make_obj_triangles(surface.surfpts,
                                                             int((1.0 / surface.delta) + 1),
                                                             int((1.0 / surface.delta) + 1),
                                                             vertex_spacing)

                # Collect vertices
                for vert_row in vertices:
                    for vert in vert_row:
                        line = "v " + str(vert.x) + " " + str(vert.y) + " " + str(vert.z) + "\n"
                        str_v.append(line)

                # Collect vertex normals
                for vert_row in vertices:
                    for vert in vert_row:
                        sn = surface.normal(vert.uv[0], vert.uv[1], True)
                        line = "vn " + str(sn[1][0]) + " " + str(sn[1][1]) + " " + str(sn[1][2]) + "\n"
                        str_vn.append(line)

                # Collect faces
                for t in triangles:
                    vl = t.vertex_ids
                    line = "f " + \
                           str(vl[0] + vertex_offset) + " " + \
                           str(vl[1] + vertex_offset) + " " + \
                           str(vl[2] + vertex_offset) + "\n"
                    str_f.append(line)

                # Update vertex offset
                vertex_offset = len(str_v)

            # Write all collected data to the file
            for line in str_v:
                fp.write(line)
            for line in str_vn:
                fp.write(line)
            for line in str_f:
                fp.write(line)
    except IOError:
        print("Cannot open " + str(file_name) + " for writing")
