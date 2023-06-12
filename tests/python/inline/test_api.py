"""Integration tests for houdini_toolbox.inline.api."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.inline.api

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_file")


# =============================================================================
# GLOBALS
# =============================================================================

OBJ = hou.node("/obj")


# =============================================================================
# TESTS
# =============================================================================


def test__get_names_in_folder():
    """Test houdini_toolbox.inline.api._get_names_in_folder."""
    node = OBJ.node("test__get_names_in_folder/null")
    parm_template = node.parm("base").parmTemplate()

    result = houdini_toolbox.inline.api._get_names_in_folder(parm_template)

    assert result == (
        "stringparm#",
        "vecparm#",
        "collapse_intparm#",
        "simple_intparm#",
        "tab_intparm1#",
        "tab_intparm2#",
        "inner_multi#",
    )


class Test_clear_caches:
    """Test houdini_toolbox.inline.api.clear_caches."""

    def test_specific(self):
        """Test clearing specific caches."""
        OBJ.node("test_clear_caches").displayNode().cook(True)
        result = hou.hscript("sopcache -l")[0].split("\n")[1]
        old_nodes = int(result.split(": ")[1])

        houdini_toolbox.inline.api.clear_caches(["SOP Cache"])

        result = hou.hscript("sopcache -l")[0].split("\n")[1]
        current_nodes = int(result.split(": ")[1])

        assert current_nodes != old_nodes

    def test_all(self):
        """Test clearing all caches."""
        OBJ.node("test_clear_caches").displayNode().cook(True)
        result = hou.hscript("sopcache -l")[0].split("\n")[1]
        old_nodes = int(result.split(": ")[1])

        houdini_toolbox.inline.api.clear_caches()

        result = hou.hscript("sopcache -l")[0].split("\n")[1]
        current_nodes = int(result.split(": ")[1])

        assert current_nodes != old_nodes


def test_run_python_statements():
    """Test houdini_toolbox.inline.api.run_python_statements."""
    if hasattr(hou.session, "pwd_test"):
        delattr(hou.session, "pwd_test")

    cwd = hou.pwd()
    hou.setPwd(hou.node("/obj"))

    code = """hou.session.pwd_test = hou.pwd()"""

    houdini_toolbox.inline.api.run_python_statements(code, use_new_context=False)

    assert hou.session.pwd_test == hou.node("/obj")

    code = """hou.session.pwd_test = hou.pwd()"""

    houdini_toolbox.inline.api.run_python_statements(code)

    assert hou.session.pwd_test == hou.node("/obj")
    assert hou.pwd() == hou.node("/obj")

    hou.setPwd(cwd)

    code = """xxx = xxx"""

    # Test when an exception occurs in the code.
    with pytest.raises(houdini_toolbox.inline.api.RunPyStatementsError):
        houdini_toolbox.inline.api.run_python_statements(code)


def test_clear_user_data(obj_test_node):
    """Test houdini_toolbox.inline.api.clear_user_data."""
    # Store the current stack since the main purpose of this function is to
    # not generate any undo entries.
    current_undo_stack = hou.undos.undoLabels()

    houdini_toolbox.inline.api.clear_user_data(obj_test_node)

    assert obj_test_node.userDataDict() == {}

    # Ensure no entries were created.
    assert hou.undos.undoLabels() == current_undo_stack


def test_has_user_data(obj_test_node):
    """Test houdini_toolbox.inline.api.has_user_data."""
    assert houdini_toolbox.inline.api.has_user_data(obj_test_node, "data_to_remove")

    assert not houdini_toolbox.inline.api.has_user_data(
        obj_test_node, "nonexistant_data"
    )

    user_data = obj_test_node.userDataDict()

    assert "data_to_remove" in user_data
    assert "nonexistant_data" not in user_data


def test_set_user_data(obj_test_node):
    """Test houdini_toolbox.inline.api.set_user_data."""
    # Store the current stack since the main purpose of this function is to
    # not generate any undo entries.
    current_undo_stack = hou.undos.undoLabels()

    assert "set_data" not in obj_test_node.userDataDict()

    houdini_toolbox.inline.api.set_user_data(obj_test_node, "set_data", "data")

    assert "set_data" in obj_test_node.userDataDict()

    # Ensure no entries were created.
    assert hou.undos.undoLabels() == current_undo_stack


def test_delete_user_data(obj_test_node):
    """Test houdini_toolbox.inline.api.delete_user_data."""
    # Store the current stack since the main purpose of this function is to
    # not generate any undo entries.
    current_undo_stack = hou.undos.undoLabels()

    assert "data_to_remove" in obj_test_node.userDataDict()

    houdini_toolbox.inline.api.delete_user_data(obj_test_node, "data_to_remove")

    assert "data_to_remove" not in obj_test_node.userDataDict()

    # Ensure no entries were created.
    assert hou.undos.undoLabels() == current_undo_stack


@pytest.mark.parametrize(
    "value_to_hash, expected",
    [
        ("foo", 143856),
        ("foo1", 5322721),
        ("fooo", 5322783),
        ("fo", 3885),
        ("123", 68982),
        ("1234", 2552386),
        ("1230", 2552382),
        ("1230", 2552382),
        ("123_123", 439236239),
        ("foo_bar", -968684932),
    ],
)
def test_hash_string(value_to_hash, expected):
    """Test houdini_toolbox.inline.api.hash_string."""
    assert houdini_toolbox.inline.api.hash_string(value_to_hash) == expected


def test_is_rendering(obj_test_node):
    """Test houdini_toolbox.inline.api.is_rendering."""
    # Force cook the node which should fail.  We manually catch the exception
    # because it comes from within Houdini and we can't patch the Python exception.
    try:
        obj_test_node.node("python").cook(force=True)

    except hou.OperationFailed:
        pass

    # The test didn't fail for some reason so we need to fail the test.
    else:
        pytest.fail("Cooking succeeded but should have failed.")

    # Execute the ROP which should cool the node and have it not fail since
    # it will be rendering.
    try:
        obj_test_node.node("render").render()

    # The cook failed for some reason so fail the test.
    except hou.OperationFailed:
        pytest.fail("Render failed but should have succeeded.")


class Test_get_global_variable_names:
    """Test houdini_toolbox.inline.api.get_global_variable_names."""

    def test(self):
        """Getting all variable names."""
        hou.hscript("set -g GLOBAL=123")
        result = houdini_toolbox.inline.api.get_global_variable_names()

        for name in ("ACTIVETAKE", "DRIVER", "E", "HIP", "GLOBAL"):
            assert name in result

    def test_dirty(self):
        """Test getting only dirty variable names."""
        name = "TEST_DIRTY_GLOBAL_VAR"

        result = houdini_toolbox.inline.api.get_global_variable_names()

        assert name not in result

        hou.hscript(f"set -g {name}=6666")

        result = houdini_toolbox.inline.api.get_global_variable_names(dirty=True)

        assert name in result

        hou.hscript("varchange")

        result = houdini_toolbox.inline.api.get_global_variable_names(dirty=True)

        assert name not in result


class Test_get_variable_names:
    """Test houdini_toolbox.inline.api.get_variable_names."""

    def test_get_variable_names(self):
        """Getting all variable names."""
        hou.hscript("set -g LOCAL=123")

        result = houdini_toolbox.inline.api.get_variable_names()

        for name in ("ACTIVETAKE", "DRIVER", "E", "HIP", "LOCAL"):
            assert name in result

    def test_get_variable_names_dirty(self):
        """Test getting only dirty variable names."""
        name = "TEST_DIRTY_LOCAL_VAR"

        result = houdini_toolbox.inline.api.get_global_variable_names()

        assert name not in result

        hou.hscript(f"set {name}=6666")

        result = houdini_toolbox.inline.api.get_variable_names(dirty=True)

        assert name in result

        hou.hscript("varchange")

        result = houdini_toolbox.inline.api.get_variable_names(dirty=True)

        assert name not in result


class Test_get_variable_value:
    """Test houdini_toolbox.inline.api.get_variable_value."""

    def test(self):
        """Test getting a variable value."""
        hip_name = houdini_toolbox.inline.api.get_variable_value("HIPNAME")

        assert hip_name == os.path.splitext(os.path.basename(hou.hipFile.path()))[0]

    def test__syntax_error(self):
        """Test when there is a syntax error."""
        hou.hscript("set ERROR_THING=1.1.1")

        result = houdini_toolbox.inline.api.get_variable_value("ERROR_THING")

        assert result == "1.1.1"


def test_set_variable():
    """Test houdini_toolbox.inline.api.set_variable."""
    value = 22
    houdini_toolbox.inline.api.set_variable("awesome", value)

    assert houdini_toolbox.inline.api.get_variable_value("awesome") == 22


def test_unset_variable():
    """Test houdini_toolbox.inline.api.unset_variable."""
    houdini_toolbox.inline.api.set_variable("tester", 10)
    houdini_toolbox.inline.api.unset_variable("tester")

    assert houdini_toolbox.inline.api.get_variable_value("tester") is None


def test_emit_var_change():
    """Test houdini_toolbox.inline.api.emit_var_change."""
    parm = hou.parm("/obj/test_emit_var_change/file1/file")

    string = "something_$VARCHANGE.bgeo"

    parm.set(string)

    path = parm.eval()

    assert path == string.replace("$VARCHANGE", "")

    houdini_toolbox.inline.api.set_variable("VARCHANGE", 22)

    houdini_toolbox.inline.api.emit_var_change()

    new_path = parm.eval()

    # Test the paths aren't the same.
    assert path != new_path

    # Test the update was successful.
    assert new_path == string.replace("$VARCHANGE", "22")


def test_expand_range():
    """Test houdini_toolbox.inline.api.expand_range."""
    values = houdini_toolbox.inline.api.expand_range("0-5 10-20:2 64 65-66")
    target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

    assert values == target


class Test_geometry_has_prims_with_shared_vertex_points:
    """Test houdini_toolbox.inline.api.geometry_has_prims_with_shared_vertex_points."""

    def test_true(self, obj_test_geo):
        """Test when the geometry does have prims with shared vertex points."""
        assert houdini_toolbox.inline.api.geometry_has_prims_with_shared_vertex_points(
            obj_test_geo
        )

    def test_false(self, obj_test_geo):
        """Test when the geometry does not have prims with shared vertex points."""
        assert (
            not houdini_toolbox.inline.api.geometry_has_prims_with_shared_vertex_points(
                obj_test_geo
            )
        )


class Test_get_primitives_with_shared_vertex_points:
    """Test houdini_toolbox.inline.api.get_primitives_with_shared_vertex_points."""

    def test_shared(self, obj_test_geo):
        """Test when the geometry does have prims with shared vertex points."""
        result = houdini_toolbox.inline.api.get_primitives_with_shared_vertex_points(
            obj_test_geo
        )
        assert result == (obj_test_geo.prims()[-1],)

    def test_none(self, obj_test_geo):
        """Test when the geometry does not have prims with shared vertex points."""
        result = houdini_toolbox.inline.api.get_primitives_with_shared_vertex_points(
            obj_test_geo
        )
        assert not result


def test_num_points(obj_test_geo):
    """Test houdini_toolbox.inline.api.num_points."""
    assert houdini_toolbox.inline.api.num_points(obj_test_geo) == 5000


def test_num_prims(obj_test_geo):
    """Test houdini_toolbox.inline.api.num_prims."""
    assert houdini_toolbox.inline.api.num_prims(obj_test_geo) == 12


class Test_sort_geometry_by_values:
    """Test houdini_toolbox.inline.api.sort_geometry_by_values."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.sort_geometry_by_values(obj_test_geo, None, [])

    def test_not_enough_points(self, obj_test_geo_copy):
        """Test when not enough points are passed."""
        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.sort_geometry_by_values(
                obj_test_geo_copy, hou.geometryType.Points, [1]
            )

    def test_not_enough_prims(self, obj_test_geo_copy):
        """Test when not enough prims are passed."""
        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.sort_geometry_by_values(
                obj_test_geo_copy, hou.geometryType.Primitives, [1, 2]
            )

    def test_invalid_geometry_type(self, obj_test_geo_copy):
        """Test when an unsupported type of geometry is passed."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.sort_geometry_by_values(
                obj_test_geo_copy, None, [1]
            )

    def test_points(self, obj_test_geo_copy):
        """Test sorting points."""
        values = obj_test_geo_copy.pointFloatAttribValues("id")

        houdini_toolbox.inline.api.sort_geometry_by_values(
            obj_test_geo_copy, hou.geometryType.Points, values
        )

        assert list(obj_test_geo_copy.pointFloatAttribValues("id")) == sorted(values)

    def test_prims(self, obj_test_geo_copy):
        """Test sorting prims."""
        values = obj_test_geo_copy.primFloatAttribValues("id")

        houdini_toolbox.inline.api.sort_geometry_by_values(
            obj_test_geo_copy, hou.geometryType.Primitives, values
        )

        assert list(obj_test_geo_copy.primFloatAttribValues("id")) == sorted(values)


def test_create_point_at_position():
    """Test houdini_toolbox.inline.api.create_point_at_position."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.create_point_at_position(
            frozen_geo, hou.Vector3(1, 2, 3)
        )

    # Success
    geo = hou.Geometry()

    point = houdini_toolbox.inline.api.create_point_at_position(
        geo, hou.Vector3(1, 2, 3)
    )

    assert point.position() == hou.Vector3(1, 2, 3)


def test_create_n_points():
    """Test houdini_toolbox.inline.api.create_n_points."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.create_n_points(frozen_geo, 15)

    # Success
    points = houdini_toolbox.inline.api.create_n_points(geo, 15)

    assert points == geo.points()

    # Invalid Number
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.create_n_points(geo, -4)


def test_merge_point_group(obj_test_geo):
    """Test houdini_toolbox.inline.api.merge_point_group."""
    geo = hou.Geometry()

    group = obj_test_geo.pointGroups()[0]

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.merge_point_group(frozen_geo, group)

    # Invalid group type
    prim_group = obj_test_geo.primGroups()[0]

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.merge_point_group(geo, prim_group)

    # Success
    houdini_toolbox.inline.api.merge_point_group(geo, group)

    assert len(geo.iterPoints()) == len(group.points())


def test_merge_points(obj_test_geo):
    """Test houdini_toolbox.inline.api.merge_points."""
    geo = hou.Geometry()

    points = obj_test_geo.globPoints("0 6 15 35-38 66")

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.merge_points(frozen_geo, points)

    # Success
    houdini_toolbox.inline.api.merge_points(geo, points)

    assert len(geo.iterPoints()) == len(points)


def test_merge_prim_group(obj_test_geo):
    """Test houdini_toolbox.inline.api.merge_prim_group."""
    geo = hou.Geometry()

    group = obj_test_geo.primGroups()[0]

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.merge_prim_group(frozen_geo, group)

    # Invalid group type
    point_group = obj_test_geo.pointGroups()[0]

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.merge_prim_group(geo, point_group)

    # Success
    houdini_toolbox.inline.api.merge_prim_group(geo, group)

    assert len(geo.iterPrims()) == len(group.prims())


def test_merge_prims(obj_test_geo):
    """Test houdini_toolbox.inline.api.merge_prims."""
    geo = hou.Geometry()

    prims = obj_test_geo.globPrims("0 6 15 35-38 66")

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.merge_prims(frozen_geo, prims)

    # Success
    houdini_toolbox.inline.api.merge_prims(geo, prims)

    assert len(geo.iterPrims()) == len(prims)


class Test_copy_packed_prims_to_points:
    """Test houdini_toolbox.inline.api.copy_packed_prims_to_points."""

    @staticmethod
    def _build_source_prims() -> hou.Geometry:
        """Build test data.

        :return: The test geometry.

        """
        geo = hou.Geometry()

        sop_category = hou.sopNodeTypeCategory()
        pack_verb = sop_category.nodeVerb("pack")

        torus_geo = hou.Geometry()
        torus_verb = sop_category.nodeVerb("torus")
        torus_verb.execute(torus_geo, [])

        pack_verb.execute(torus_geo, [torus_geo])

        geo.merge(torus_geo)

        box_geo = hou.Geometry()
        box_verb = sop_category.nodeVerb("box")
        box_verb.execute(box_geo, [])

        pack_verb.execute(box_geo, [box_geo])

        geo.merge(box_geo)
        geo.merge(box_geo)

        id_attrib = geo.addAttrib(hou.attribType.Prim, "orig_id", (1,))
        other_attrib = geo.addAttrib(hou.attribType.Prim, "other", ("",))

        for idx, prim in enumerate(geo.prims()):
            prim.setAttribValue(id_attrib, idx)
            prim.setAttribValue(other_attrib, "foo")

            group = geo.createPrimGroup(f"group{idx}")
            group.add(prim)

        return geo

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        source_geo = self._build_source_prims()

        prim_order = [2, 0, 1]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.copy_packed_prims_to_points(
                obj_test_geo,
                source_geo,
                prim_order,
                list(range(3)),
            )

    def test_size_mismatch(self, obj_test_geo_copy):
        """Test when there is a size mismatch the the number of elements passed."""
        source_geo = self._build_source_prims()

        prim_order = [2, 0, 1]

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.copy_packed_prims_to_points(
                obj_test_geo_copy,
                source_geo,
                prim_order,
                list(range(2)),
            )

    def test_copy_all(self, obj_test_geo_copy):
        """Test copying with all attributes and groups."""
        source_geo = self._build_source_prims()

        prim_order = [2, 0, 1]

        houdini_toolbox.inline.api.copy_packed_prims_to_points(
            obj_test_geo_copy,
            source_geo,
            prim_order,
            list(range(3)),
        )

        assert len(obj_test_geo_copy.iterPoints()) == 3
        assert len(obj_test_geo_copy.iterPrims()) == 3

        for pt_idx in range(3):
            pr_idx = prim_order[pt_idx]
            prim = obj_test_geo_copy.iterPrims()[pt_idx]
            pt = obj_test_geo_copy.iterPoints()[pt_idx]

            xform = prim.fullTransform()

            orient = hou.Quaternion(pt.attribValue("orient"))
            assert xform.extractTranslates() == pt.position()
            assert xform.extractRotationMatrix3() == orient.extractRotationMatrix3()

            assert prim.attribValue("orig_id") == pr_idx
            assert prim.attribValue("other") == "foo"

            group = obj_test_geo_copy.findPrimGroup(f"group{pr_idx}")
            assert prim in group.prims()

    def test_copy_none(self, obj_test_geo_copy):
        """Test copying with no attributes or groups."""
        source_geo = self._build_source_prims()

        prim_order = [2, 0, 1]

        houdini_toolbox.inline.api.copy_packed_prims_to_points(
            obj_test_geo_copy,
            source_geo,
            prim_order,
            list(range(3)),
            copy_attribs=False,
            copy_groups=False,
        )

        assert len(obj_test_geo_copy.iterPoints()) == 3
        assert len(obj_test_geo_copy.iterPrims()) == 3

        assert len(obj_test_geo_copy.primGroups()) == 0
        assert len(obj_test_geo_copy.primAttribs()) == 0

        for pt_idx in range(3):
            prim = obj_test_geo_copy.iterPrims()[pt_idx]
            pt = obj_test_geo_copy.iterPoints()[pt_idx]

            xform = prim.fullTransform()

            orient = hou.Quaternion(pt.attribValue("orient"))
            assert xform.extractTranslates() == pt.position()
            assert xform.extractRotationMatrix3() == orient.extractRotationMatrix3()

    def test_copy_some(self, obj_test_geo_copy):
        """Test copying with specific attributes and groups."""
        source_geo = self._build_source_prims()

        group_to_copy = source_geo.findPrimGroup("group1")
        attrib_to_copy = source_geo.findPrimAttrib("orig_id")

        prim_order = [2, 0, 1]

        houdini_toolbox.inline.api.copy_packed_prims_to_points(
            obj_test_geo_copy,
            source_geo,
            prim_order,
            list(range(3)),
            attribs=[attrib_to_copy],
            groups=[group_to_copy],
        )

        assert len(obj_test_geo_copy.iterPoints()) == 3
        assert len(obj_test_geo_copy.iterPrims()) == 3

        assert len(obj_test_geo_copy.primGroups()) == 1
        assert len(obj_test_geo_copy.primAttribs()) == 1

        for pt_idx in range(3):
            pr_idx = prim_order[pt_idx]
            prim = obj_test_geo_copy.iterPrims()[pt_idx]
            pt = obj_test_geo_copy.iterPoints()[pt_idx]

            xform = prim.fullTransform()

            orient = hou.Quaternion(pt.attribValue("orient"))
            assert xform.extractTranslates() == pt.position()
            assert xform.extractRotationMatrix3() == orient.extractRotationMatrix3()

            assert prim.attribValue("orig_id") == pr_idx

            group = obj_test_geo_copy.findPrimGroup(group_to_copy.name())

            if prim.attribValue("orig_id") == int(group_to_copy.name()[-1]):
                assert prim in group.prims()
            else:
                assert prim not in group.prims()


class Test_copy_attribute_values:
    """Test houdini_toolbox.inline.api.copy_attribute_values."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        geo = hou.Geometry().freeze(True)
        attribs = obj_test_geo.globalAttribs()

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.copy_attribute_values(obj_test_geo, attribs, geo)

    def test_points(self, obj_test_geo):
        """Test copying attribute values between two points."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()

        houdini_toolbox.inline.api.copy_attribute_values(
            obj_test_geo.iterPoints()[2], attribs, pt1
        )
        houdini_toolbox.inline.api.copy_attribute_values(
            obj_test_geo.iterPoints()[6], attribs, pt2
        )

        # Ensure all the attributes got copied right.
        assert len(geo.pointAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pt1.position().isAlmostEqual(hou.Vector3(1.66667, 0, -5))
        assert pt2.position().isAlmostEqual(hou.Vector3(1.66667, 0, -1.66667))

    def test_prims(self, obj_test_geo):
        """Test copying attribute values between two prims."""
        attribs = obj_test_geo.primAttribs()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()

        houdini_toolbox.inline.api.copy_attribute_values(
            obj_test_geo.iterPrims()[1], attribs, pr1
        )
        houdini_toolbox.inline.api.copy_attribute_values(
            obj_test_geo.iterPrims()[4], attribs, pr2
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pr1.attribValue("prnum") == 1
        assert pr2.attribValue("prnum") == 4

    def test_vertex_to_point(self, obj_test_geo):
        """Test copying attributes values from a vertex to a point."""
        attribs = obj_test_geo.vertexAttribs()

        geo = hou.Geometry()
        pt1 = geo.createPoint()

        pr1 = obj_test_geo.prims()[1]

        houdini_toolbox.inline.api.copy_attribute_values(pr1.vertex(2), attribs, pt1)
        assert pt1.attribValue("id") == 6
        assert pt1.attribValue("random_vtx") == 0.031702518463134766

    def test_points_to_global(self, obj_test_geo):
        """Test copying attributes values from a point to a detail."""
        attribs = obj_test_geo.pointAttribs()
        geo = hou.Geometry()

        houdini_toolbox.inline.api.copy_attribute_values(
            obj_test_geo.iterPoints()[2], attribs, geo
        )

        # Ensure all the attributes got copied right.
        assert len(geo.globalAttribs()) == len(attribs)

        assert geo.attribValue("ptnum") == 2

        assert geo.attribValue("random") == 0.5108950138092041

    def test_global_to_point(self, obj_test_geo):
        """Test copying attributes values from a detail to a point."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()
        pt1 = geo.createPoint()

        houdini_toolbox.inline.api.copy_attribute_values(obj_test_geo, attribs, pt1)

        assert pt1.attribValue("barbles") == 33
        assert pt1.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_global(self, obj_test_geo):
        """Test copying attribute values between two details."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()

        houdini_toolbox.inline.api.copy_attribute_values(obj_test_geo, attribs, geo)
        assert geo.attribValue("barbles") == 33
        assert geo.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_vertex(self, obj_test_geo):
        """Test copying attributes values from a detail to a vertex."""
        attribs = obj_test_geo.globalAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pr1 = geo.createPolygon()
        pr1.addVertex(pt1)
        vtx1 = pr1.vertex(0)

        houdini_toolbox.inline.api.copy_attribute_values(obj_test_geo, attribs, vtx1)
        assert vtx1.attribValue("barbles") == 33
        assert vtx1.attribValue("foobles") == (1.0, 2)


class Test_batch_copy_attributes_by_indices:
    """Test houdini_toolbox.inline.api.batch_copy_attributes_by_indices"""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        geo.createPoint()
        geo.createPoint()

        geo = geo.freeze(True)

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
                obj_test_geo, hou.Point, [2, 6], attribs, geo, hou.Point, [0, 1]
            )

    def test_size_mismatch(self, obj_test_geo):
        """Test when there is a size mismatch the the number of elements passed."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        geo.createPoint()
        geo.createPoint()

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
                obj_test_geo, hou.Point, [2], attribs, geo, hou.Point, [0, 1]
            )

    def test_copy_points(self, obj_test_geo):
        """Test copying attribute values between sets of points."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo, hou.Point, [2, 6], attribs, geo, hou.Point, [0, 1]
        )

        # Ensure all the attributes got copied right.
        assert len(geo.pointAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pt1.position().isAlmostEqual(hou.Vector3(1.66667, 0, -5))
        assert pt2.position().isAlmostEqual(hou.Vector3(1.66667, 0, -1.66667))

    def test_copy_prims(self, obj_test_geo):
        """Test copying attribute values between sets of prims."""
        attribs = obj_test_geo.primAttribs()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo, hou.Prim, [1, 4], attribs, geo, hou.Prim, [0, 1]
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pr1.attribValue("prnum") == 1
        assert pr2.attribValue("prnum") == 4

    def test_vertex_to_point(self, obj_test_geo):
        """Test copying attributes values from vertices to points."""
        attribs = obj_test_geo.vertexAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()

        pr1 = obj_test_geo.prims()[1]

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo,
            hou.Vertex,
            [pr1.vertex(2).linearNumber()],
            attribs,
            geo,
            hou.Point,
            [0],
        )

        assert pt1.attribValue("id") == 6
        assert pt1.attribValue("random_vtx") == 0.031702518463134766

    def test_points_to_global(self, obj_test_geo):
        """Test copying attributes values from a single point to a detail."""
        attribs = obj_test_geo.pointAttribs()
        geo = hou.Geometry()

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo, hou.Point, [2], attribs, geo, hou.Geometry, [0]
        )

        # Ensure all the attributes got copied right.
        assert len(geo.globalAttribs()) == len(attribs)

        assert geo.attribValue("ptnum") == 2

        assert geo.attribValue("random") == 0.5108950138092041

    def test_global_to_points(self, obj_test_geo):
        """Test copying attributes values from a detail to a single point."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()
        pt1 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo, hou.Geometry, [0], attribs, geo, hou.Point, [0]
        )

        assert pt1.attribValue("barbles") == 33
        assert pt1.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_global(self, obj_test_geo):
        """Test copying attributes values between two details."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo, hou.Geometry, [0], attribs, geo, hou.Geometry, [0]
        )
        assert geo.attribValue("barbles") == 33
        assert geo.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_vertex(self, obj_test_geo):
        """Test copying attributes values from a detail to a single vertex."""
        attribs = obj_test_geo.globalAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pr1 = geo.createPolygon()
        pr1.addVertex(pt1)
        vtx1 = pr1.vertex(0)

        houdini_toolbox.inline.api.batch_copy_attributes_by_indices(
            obj_test_geo,
            hou.Geometry,
            [0],
            attribs,
            geo,
            hou.Vertex,
            [vtx1.linearNumber()],
        )
        assert vtx1.attribValue("barbles") == 33
        assert vtx1.attribValue("foobles") == (1.0, 2)


class Test_batch_copy_attrib_values:
    """Test houdini_toolbox.inline.api.batch_copy_attrib_values"""

    def test_size_mismatch(self, obj_test_geo):
        """Test when there is a size mismatch the the number of elements passed."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()

        geo.freeze(True)

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.batch_copy_attrib_values(
                [obj_test_geo.iterPoints()[2]], attribs, [pt1, pt2]
            )

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        geo.createPoint()
        geo.createPoint()

        geo = geo.freeze(True)
        pt1 = geo.iterPoints()[0]
        pt2 = geo.iterPoints()[1]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.batch_copy_attrib_values(
                [obj_test_geo.iterPoints()[2], obj_test_geo.iterPoints()[6]],
                attribs,
                [pt1, pt2],
            )

    def test_copy_points(self, obj_test_geo):
        """Test copying attribute values between sets of points."""
        attribs = obj_test_geo.pointAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo.iterPoints()[2], obj_test_geo.iterPoints()[6]],
            attribs,
            [pt1, pt2],
        )

        # Ensure all the attributes got copied right.
        assert len(geo.pointAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pt1.position().isAlmostEqual(hou.Vector3(1.66667, 0, -5))
        assert pt2.position().isAlmostEqual(hou.Vector3(1.66667, 0, -1.66667))

    def test_copy_prims(self, obj_test_geo):
        """Test copying attribute values between sets of points."""
        attribs = obj_test_geo.primAttribs()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo.iterPrims()[1], obj_test_geo.iterPrims()[4]],
            attribs,
            [pr1, pr2],
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primAttribs()) == len(attribs)

        # Ensure P got copied right.
        assert pr1.attribValue("prnum") == 1
        assert pr2.attribValue("prnum") == 4

    def test_vertex_to_point(self, obj_test_geo):
        """Test copying attribute values between a vertex and a point."""
        attribs = obj_test_geo.vertexAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()

        pr1 = obj_test_geo.prims()[1]

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [pr1.vertex(2)], attribs, [pt1]
        )
        assert pt1.attribValue("id") == 6
        assert pt1.attribValue("random_vtx") == 0.031702518463134766

    def test_points_to_global(self, obj_test_geo):
        """Test copying attribute values between a point and a detail."""
        attribs = obj_test_geo.pointAttribs()
        geo = hou.Geometry()

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo.iterPoints()[2]], attribs, [geo]
        )

        # Ensure all the attributes got copied right.
        assert len(geo.globalAttribs()) == len(attribs)

        assert geo.attribValue("ptnum") == 2

        assert geo.attribValue("random") == 0.5108950138092041

    def test_global_to_points(self, obj_test_geo):
        """Test copying attribute values between a detail and a point."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()
        pt1 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo], attribs, [pt1]
        )

        assert pt1.attribValue("barbles") == 33
        assert pt1.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_global(self, obj_test_geo):
        """Test copying attribute values between two details."""
        geo = hou.Geometry()
        attribs = obj_test_geo.globalAttribs()

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo], attribs, [geo]
        )
        assert geo.attribValue("barbles") == 33
        assert geo.attribValue("foobles") == (1.0, 2.0)

    def test_global_to_vertex(self, obj_test_geo):
        """Test copying attribute values between a detail and a vertex."""
        attribs = obj_test_geo.globalAttribs()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pr1 = geo.createPolygon()
        pr1.addVertex(pt1)
        vtx1 = pr1.vertex(0)

        houdini_toolbox.inline.api.batch_copy_attrib_values(
            [obj_test_geo], attribs, [vtx1]
        )
        assert vtx1.attribValue("barbles") == 33
        assert vtx1.attribValue("foobles") == (1.0, 2)


class Test_copy_group_membership:
    """Test houdini_toolbox.inline.api.copy_group_membership."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        geo = hou.Geometry().freeze(True)
        groups = obj_test_geo.pointGroups()

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.copy_group_membership(obj_test_geo, groups, geo)

    def test_points(self, obj_test_geo):
        """Test copying group membership between points."""
        groups = obj_test_geo.pointGroups()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()
        pt3 = geo.createPoint()

        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPoints()[2], groups, pt1
        )
        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPoints()[8], groups, pt2
        )
        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPoints()[10], groups, pt3
        )

        # Ensure all the groups got copied right.
        assert len(geo.pointGroups()) == len(groups)

        group1 = geo.findPointGroup("point_group1")
        group2 = geo.findPointGroup("point_group2")

        assert pt1 in group1.points()
        assert pt1 not in group2.points()

        assert pt2 in group1.points()
        assert pt2 in group2.points()

        assert pt3 in group2.points()
        assert pt3 not in group1.points()

    def test_prims(self, obj_test_geo):
        """Test copying group membership between prims."""
        groups = obj_test_geo.primGroups()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()
        pr3 = geo.createPolygon()

        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPrims()[1], groups, pr1
        )
        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPrims()[4], groups, pr2
        )
        houdini_toolbox.inline.api.copy_group_membership(
            obj_test_geo.iterPrims()[5], groups, pr3
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primGroups()) == len(groups)

        group1 = geo.findPrimGroup("prim_group1")
        group2 = geo.findPrimGroup("prim_group2")

        assert pr1 in group1.prims()
        assert pr1 not in group2.prims()

        assert pr2 in group1.prims()
        assert pr2 in group2.prims()

        assert pr3 in group2.prims()
        assert pr3 not in group1.prims()


class Test_batch_copy_group_membership_by_indices:
    """Test houdini_toolbox.inline.api.batch_copy_group_membership_by_indices."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        geo = hou.Geometry().freeze(True)
        groups = obj_test_geo.pointGroups()

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.batch_copy_group_membership_by_indices(
                obj_test_geo, hou.Point, [0], groups, geo, hou.Point, [0]
            )

    def test_size_mismatch(self, obj_test_geo):
        """Test when there is a size mismatch the the number of elements passed."""
        groups = obj_test_geo.pointGroups()

        geo = hou.Geometry()

        geo.createPoint()
        geo.createPoint()
        geo.createPoint()

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.batch_copy_group_membership_by_indices(
                obj_test_geo, hou.Point, [2, 8], groups, geo, hou.Point, [0, 2, 1]
            )

    def test_points(self, obj_test_geo):
        """Test copying group membership between points."""
        groups = obj_test_geo.pointGroups()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()
        pt3 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_group_membership_by_indices(
            obj_test_geo, hou.Point, [2, 8, 10], groups, geo, hou.Point, [0, 2, 1]
        )

        # Ensure all the groups got copied right.
        assert len(geo.pointGroups()) == len(groups)

        group1 = geo.findPointGroup("point_group1")
        group2 = geo.findPointGroup("point_group2")

        assert pt1 in group1.points()
        assert pt1 not in group2.points()

        assert pt3 in group1.points()
        assert pt3 in group2.points()

        assert pt2 in group2.points()
        assert pt2 not in group1.points()

    def test_prims(self, obj_test_geo):
        """Test copying group membership between prims."""
        groups = obj_test_geo.primGroups()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()
        pr3 = geo.createPolygon()

        houdini_toolbox.inline.api.batch_copy_group_membership_by_indices(
            obj_test_geo, hou.Prim, [1, 4, 5], groups, geo, hou.Prim, [0, 1, 2]
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primGroups()) == len(groups)

        group1 = geo.findPrimGroup("prim_group1")
        group2 = geo.findPrimGroup("prim_group2")

        assert pr1 in group1.prims()
        assert pr1 not in group2.prims()

        assert pr2 in group1.prims()
        assert pr2 in group2.prims()

        assert pr3 in group2.prims()
        assert pr3 not in group1.prims()


class Test_batch_copy_group_membership:
    """Test houdini_toolbox.inline.api.batch_copy_group_membership."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        geo = hou.Geometry()
        geo.createPoint()

        geo = geo.freeze(True)

        groups = obj_test_geo.pointGroups()

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.batch_copy_group_membership(
                [obj_test_geo.points()[0]], groups, [geo.points()[0]]
            )

    def test_size_mismatch(self, obj_test_geo):
        """Test when there is a size mismatch the the number of elements passed."""
        groups = obj_test_geo.pointGroups()

        geo = hou.Geometry()

        geo.createPoint()
        geo.createPoint()
        geo.createPoint()

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.batch_copy_group_membership(
                [obj_test_geo.points()[0], obj_test_geo.points()[8]],
                groups,
                [geo.points()[0]],
            )

    def test_points(self, obj_test_geo):
        """Test copying group membership between points."""
        groups = obj_test_geo.pointGroups()

        geo = hou.Geometry()

        pt1 = geo.createPoint()
        pt2 = geo.createPoint()
        pt3 = geo.createPoint()

        houdini_toolbox.inline.api.batch_copy_group_membership(
            obj_test_geo.globPoints("2 8 10"), groups, geo.points()
        )

        # Ensure all the groups got copied right.
        assert len(geo.pointGroups()) == len(groups)

        group1 = geo.findPointGroup("point_group1")
        group2 = geo.findPointGroup("point_group2")

        assert pt1 in group1.points()
        assert pt1 not in group2.points()

        assert pt2 in group1.points()
        assert pt2 in group2.points()

        assert pt3 in group2.points()
        assert pt3 not in group1.points()

    def test_prims(self, obj_test_geo):
        """Test copying group membership between prims."""
        groups = obj_test_geo.primGroups()

        geo = hou.Geometry()

        pr1 = geo.createPolygon()
        pr2 = geo.createPolygon()
        pr3 = geo.createPolygon()

        houdini_toolbox.inline.api.batch_copy_group_membership(
            obj_test_geo.globPrims("1 4 5"), groups, geo.prims()
        )

        # Ensure all the attributes got copied right.
        assert len(geo.primGroups()) == len(groups)

        group1 = geo.findPrimGroup("prim_group1")
        group2 = geo.findPrimGroup("prim_group2")

        assert pr1 in group1.prims()
        assert pr1 not in group2.prims()

        assert pr2 in group1.prims()
        assert pr2 in group2.prims()

        assert pr3 in group2.prims()
        assert pr3 not in group1.prims()


def test_point_adjacent_polygons(obj_test_geo):
    """Test houdini_toolbox.inline.api.point_adjacent_polygons."""
    target = obj_test_geo.globPrims("1 2")

    prims = houdini_toolbox.inline.api.point_adjacent_polygons(
        obj_test_geo.iterPrims()[0]
    )

    assert prims == target


def test_edge_adjacent_polygons(obj_test_geo):
    """Test houdini_toolbox.inline.api.edge_adjacent_polygons."""
    target = obj_test_geo.globPrims("2")

    prims = houdini_toolbox.inline.api.edge_adjacent_polygons(
        obj_test_geo.iterPrims()[0]
    )

    assert prims == target


def test_connected_points(obj_test_geo):
    """Test houdini_toolbox.inline.api.connected_points."""
    target = obj_test_geo.globPoints("1 3 5 7")

    points = houdini_toolbox.inline.api.connected_points(obj_test_geo.iterPoints()[4])

    assert points == target


def test_prims_connected_to_point(obj_test_geo):
    """Test houdini_toolbox.inline.api.connected_prims."""
    target = obj_test_geo.prims()

    prims = houdini_toolbox.inline.api.prims_connected_to_point(
        obj_test_geo.iterPoints()[4]
    )

    assert prims == target


def test_referencing_vertices(obj_test_geo):
    """Test houdini_toolbox.inline.api.referencing_vertices."""
    target = obj_test_geo.globVertices("0v2 1v3 2v1 3v0")

    vertices = houdini_toolbox.inline.api.referencing_vertices(
        obj_test_geo.iterPoints()[4]
    )

    assert vertices == target


class Test_string_table_indices:
    """Test houdini_toolbox.inline.api.string_table_indices."""

    def test_not_string_attrib(self, obj_test_geo):
        """Test when the attribute is not a string attribute."""
        attr = obj_test_geo.findPointAttrib("not_string")

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.string_table_indices(attr)

    def test_point_attrib(self, obj_test_geo):
        """Test getting the indices of a point attribute."""
        target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1)

        attr = obj_test_geo.findPointAttrib("test")

        assert houdini_toolbox.inline.api.string_table_indices(attr) == target

    def test_prim_attrib(self, obj_test_geo):
        """Test getting the indices of a prim attribute."""
        target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4)

        attr = obj_test_geo.findPrimAttrib("test")

        assert houdini_toolbox.inline.api.string_table_indices(attr) == target


def test_vertex_string_attrib_values(obj_test_geo):
    """Test houdini_toolbox.inline.api.vertex_string_attrib_values."""
    with pytest.raises(hou.OperationFailed):
        assert houdini_toolbox.inline.api.vertex_string_attrib_values(
            obj_test_geo, "foo"
        )

    with pytest.raises(ValueError):
        assert houdini_toolbox.inline.api.vertex_string_attrib_values(
            obj_test_geo, "not_string"
        )

    target = (
        "vertex0",
        "vertex1",
        "vertex2",
        "vertex3",
        "vertex4",
        "vertex5",
        "vertex6",
        "vertex7",
    )

    assert (
        houdini_toolbox.inline.api.vertex_string_attrib_values(obj_test_geo, "test")
        == target
    )


class Test_set_vertex_string_attrib_values:
    """Test houdini_toolbox.inline.api.set_vertex_string_attrib_values."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.set_vertex_string_attrib_values(
                obj_test_geo, "test", ()
            )

    def test(self, obj_test_geo_copy):
        """Test setting the values from a list."""
        target = ("vertex0", "vertex1", "vertex2", "vertex3", "vertex4")

        attr = obj_test_geo_copy.findVertexAttrib("test")

        houdini_toolbox.inline.api.set_vertex_string_attrib_values(
            obj_test_geo_copy, "test", target
        )

        values = []

        for prim in obj_test_geo_copy.prims():
            values.extend([vertex.attribValue(attr) for vertex in prim.vertices()])

        assert tuple(values) == target

    def test_no_attribute(self, obj_test_geo_copy):
        """Test when the attribute does not exist."""
        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.set_vertex_string_attrib_values(
                obj_test_geo_copy, "thing", ()
            )

    def test_not_string_attribute(self, obj_test_geo_copy):
        """Test when the attribute is not a string attribute."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_vertex_string_attrib_values(
                obj_test_geo_copy, "notstring", ()
            )

    def test_invalid_attribute_size(self, obj_test_geo_copy):
        """Test when the number of values does not match the number of  vertices."""
        target = ("vertex0", "vertex1", "vertex2", "vertex3")

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_vertex_string_attrib_values(
                obj_test_geo_copy, "test", target
            )


class Test_set_shared_point_string_attrib:
    """Test houdini_toolbox.inline.api.set_shared_point_string_attrib."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.set_shared_point_string_attrib(
                obj_test_geo, "foo", "point0"
            )

    def test_no_attribute(self, obj_test_geo_copy):
        """Test when the attribute does not exist."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_shared_point_string_attrib(
                obj_test_geo_copy, "foo", "point0"
            )

    def test_not_string_attribute(self, obj_test_geo_copy):
        """Test when the attribute is not a string attribute."""
        obj_test_geo_copy.addAttrib(hou.attribType.Point, "not_string", 0)

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_shared_point_string_attrib(
                obj_test_geo_copy, "not_string", "point0"
            )

    def test(self, obj_test_geo_copy):
        """Test setting the values."""
        target = ["point0"] * 10

        houdini_toolbox.inline.api.set_shared_point_string_attrib(
            obj_test_geo_copy, "test", "point0"
        )

        assert list(obj_test_geo_copy.pointStringAttribValues("test")) == target

    def test_group(self, obj_test_geo_copy):
        """Test setting only the values of the group."""
        target = ["point0"] * 5 + [""] * 5

        group = obj_test_geo_copy.pointGroups()[0]

        houdini_toolbox.inline.api.set_shared_point_string_attrib(
            obj_test_geo_copy, "test", "point0", group
        )

        assert list(obj_test_geo_copy.pointStringAttribValues("test")) == target


class Test_set_shared_prim_string_attrib:
    """Test houdini_toolbox.inline.api.set_shared_prim_string_attrib."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.set_shared_prim_string_attrib(
                obj_test_geo, "test", "prim0"
            )

    def test_no_attribute(self, obj_test_geo_copy):
        """Test when the attribute does not exist."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_shared_prim_string_attrib(
                obj_test_geo_copy, "foo", "prim0"
            )

    def test_not_string_attribute(self, obj_test_geo_copy):
        """Test when the attribute is not a string attribute."""
        obj_test_geo_copy.addAttrib(hou.attribType.Prim, "not_string", 0)

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_shared_prim_string_attrib(
                obj_test_geo_copy, "not_string", "value"
            )

    def test(self, obj_test_geo_copy):
        """Test setting the values."""
        target = ["value"] * 5

        attr = obj_test_geo_copy.findPrimAttrib("test")

        houdini_toolbox.inline.api.set_shared_prim_string_attrib(
            obj_test_geo_copy, attr.name(), "value"
        )

        assert list(obj_test_geo_copy.primStringAttribValues("test")) == target

    def test_group(self, obj_test_geo_copy):
        """Test setting only the values of the group."""
        target = ["value"] * 3 + ["", ""]

        attr = obj_test_geo_copy.findPrimAttrib("test")

        group = obj_test_geo_copy.findPrimGroup("group1")

        houdini_toolbox.inline.api.set_shared_prim_string_attrib(
            obj_test_geo_copy, attr.name(), "value", group
        )

        assert list(obj_test_geo_copy.primStringAttribValues("test")) == target


class Test_attribute_has_uninitialized_string_values:
    """Test houdini_toolbox.inline.api.attribute_has_uninitialized_string_values."""

    def test_not_string_attribute(self, obj_test_geo):
        """Test when the attribute is not a string attribute."""
        attrib = obj_test_geo.findPointAttrib("not_string_attrib")

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.attribute_has_uninitialized_string_values(attrib)

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("point_attrib_fully_initialized", False),
            ("point_attrib_not_initialized", True),
            ("point_attrib_partially_initialized", True),
        ],
    )
    def test_point_attribs(self, obj_test_geo, name, expected):
        """Test point attributes."""
        attrib = obj_test_geo.findPointAttrib(name)

        result = houdini_toolbox.inline.api.attribute_has_uninitialized_string_values(
            attrib
        )

        assert result == expected

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("prim_attrib_fully_initialized", False),
            ("prim_attrib_not_initialized", True),
            ("prim_attrib_partially_initialized", True),
        ],
    )
    def test_prim_attribs(self, obj_test_geo, name, expected):
        """Test prim attributes."""
        attrib = obj_test_geo.findPrimAttrib(name)

        result = houdini_toolbox.inline.api.attribute_has_uninitialized_string_values(
            attrib
        )

        assert result == expected

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("vertex_attrib_fully_initialized", False),
            ("vertex_attrib_not_initialized", True),
            ("vertex_attrib_partially_initialized", True),
        ],
    )
    def test_vertex_attribs(self, obj_test_geo, name, expected):
        """Test vertex attributes."""
        attrib = obj_test_geo.findVertexAttrib(name)

        result = houdini_toolbox.inline.api.attribute_has_uninitialized_string_values(
            attrib
        )

        assert result == expected

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("detail_attrib_fully_initialized", False),
            ("detail_attrib_not_initialized", True),
        ],
    )
    def test_detail_attribs(self, obj_test_geo, name, expected):
        """Test detail attributes."""
        attrib = obj_test_geo.findGlobalAttrib(name)

        result = houdini_toolbox.inline.api.attribute_has_uninitialized_string_values(
            attrib
        )

        assert result == expected


def test_face_has_edge(obj_test_geo):
    """Test houdini_toolbox.inline.api.face_has_edge."""
    face = obj_test_geo.iterPrims()[0]

    pt0 = obj_test_geo.iterPoints()[0]
    pt1 = obj_test_geo.iterPoints()[1]

    assert houdini_toolbox.inline.api.face_has_edge(face, pt0, pt1)

    # False
    face = obj_test_geo.iterPrims()[0]

    pt0 = obj_test_geo.iterPoints()[0]
    pt2 = obj_test_geo.iterPoints()[2]

    assert houdini_toolbox.inline.api.face_has_edge(face, pt0, pt2)


def test_shared_edges(obj_test_geo):
    """Test houdini_toolbox.inline.api.shared_edges."""
    pr0, pr1 = obj_test_geo.prims()

    edges = houdini_toolbox.inline.api.shared_edges(pr0, pr1)

    pt2 = obj_test_geo.iterPoints()[2]
    pt3 = obj_test_geo.iterPoints()[3]

    edge = obj_test_geo.findEdge(pt2, pt3)

    assert edges == (edge,)


class Test_insert_vertex:
    """Test houdini_toolbox.inline.api.insert_vertex."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        face = obj_test_geo.iterPrims()[0]

        pt0 = obj_test_geo.points()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.insert_vertex(face, pt0, 2)

    def test_negative_index(self, obj_test_geo_copy):
        """Test when the index to insert at is negative."""
        face = obj_test_geo_copy.iterPrims()[0]

        new_point = houdini_toolbox.inline.api.create_point_at_position(
            obj_test_geo_copy, hou.Vector3(0.5, 0, 0.5)
        )

        with pytest.raises(IndexError):
            houdini_toolbox.inline.api.insert_vertex(face, new_point, -1)

    def test_invalid_index(self, obj_test_geo_copy):
        """Test when the index is greater than or equal to the number of vertices"""
        face = obj_test_geo_copy.iterPrims()[0]

        new_point = houdini_toolbox.inline.api.create_point_at_position(
            obj_test_geo_copy, hou.Vector3(0.5, 0, 0.5)
        )

        with pytest.raises(IndexError):
            houdini_toolbox.inline.api.insert_vertex(face, new_point, 10)

    def test(self, obj_test_geo_copy):
        """Test inserting a vertex."""
        face = obj_test_geo_copy.iterPrims()[0]

        new_point = houdini_toolbox.inline.api.create_point_at_position(
            obj_test_geo_copy, hou.Vector3(0.5, 0, 0.5)
        )

        houdini_toolbox.inline.api.insert_vertex(face, new_point, 2)

        assert face.vertex(2).point() == new_point


class Test_delete_vertex:
    """Test houdini_toolbox.inline.api.delete_vertex_from_face."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        face = obj_test_geo.iterPrims()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.delete_vertex_from_face(face, 3)

    def test_negative_index(self, obj_test_geo_copy):
        """Test when the index to delete is negative."""
        face = obj_test_geo_copy.iterPrims()[0]

        with pytest.raises(IndexError):
            houdini_toolbox.inline.api.delete_vertex_from_face(face, -1)

    def test_invalid_index(self, obj_test_geo_copy):
        """Test when the index is greater than or equal to the number of vertices"""
        face = obj_test_geo_copy.iterPrims()[0]

        with pytest.raises(IndexError):
            houdini_toolbox.inline.api.delete_vertex_from_face(face, 10)

    def test(self, obj_test_geo_copy):
        """Test deleting a vertex."""
        face = obj_test_geo_copy.iterPrims()[0]

        houdini_toolbox.inline.api.delete_vertex_from_face(face, 3)

        assert len(face.vertices()) == 3


def test_set_face_vertex_point(obj_test_geo, obj_test_geo_copy):
    """Test houdini_toolbox.inline.api.set_face_vertex_point."""
    face = obj_test_geo.iterPrims()[0]
    pt4 = obj_test_geo.iterPoints()[4]

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.set_face_vertex_point(face, 3, pt4)

    face = obj_test_geo_copy.iterPrims()[0]
    pt4 = obj_test_geo_copy.iterPoints()[4]

    houdini_toolbox.inline.api.set_face_vertex_point(face, 3, pt4)

    assert face.vertex(3).point().number() == 4

    # Negative index.
    with pytest.raises(IndexError):
        houdini_toolbox.inline.api.set_face_vertex_point(face, -1, pt4)

    # Invalid index.
    with pytest.raises(IndexError):
        houdini_toolbox.inline.api.set_face_vertex_point(face, 10, pt4)


def test_primitive_bary_center(obj_test_geo):
    """Test houdini_toolbox.inline.api.primitive_bary_center."""
    target = hou.Vector3(1.5, 1, -1)

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_toolbox.inline.api.primitive_bary_center(prim) == target


def test_primitive_area(obj_test_geo):
    """Test houdini_toolbox.inline.api.primitive_area."""
    target = 4.375
    prim = obj_test_geo.iterPrims()[0]

    assert houdini_toolbox.inline.api.primitive_area(prim) == target


def test_primitive_perimeter(obj_test_geo):
    """Test houdini_toolbox.inline.api.primitive_perimeter."""
    target = 6.5

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_toolbox.inline.api.primitive_perimeter(prim) == target


def test_primitive_volume(obj_test_geo):
    """Test houdini_toolbox.inline.api.primitive_volume."""
    target = 0.1666666716337204

    prim = obj_test_geo.iterPrims()[0]

    assert hou.almostEqual(houdini_toolbox.inline.api.primitive_volume(prim), target)


class Test_reverse_prim:
    """Test houdini_toolbox.inline.api.reverse_prim."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        prim = obj_test_geo.iterPrims()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.reverse_prim(prim)

    def test(self, obj_test_geo_copy):
        """Test reversing the vertex order."""
        target = hou.Vector3(0, -1, 0)

        prim = obj_test_geo_copy.iterPrims()[0]
        houdini_toolbox.inline.api.reverse_prim(prim)

        assert prim.normal() == target


def test_check_minimum_polygon_vertex_count(obj_test_geo):
    """Test houdini_toolbox.inline.api.check_minimum_polygon_vertex_count."""
    assert houdini_toolbox.inline.api.check_minimum_polygon_vertex_count(
        obj_test_geo, 3
    )

    assert not houdini_toolbox.inline.api.check_minimum_polygon_vertex_count(
        obj_test_geo, 3, ignore_open=False
    )

    assert not houdini_toolbox.inline.api.check_minimum_polygon_vertex_count(
        obj_test_geo, 5
    )


def test_primitive_bounding_box(obj_test_geo):
    """Test houdini_toolbox.inline.api.primitive_bounding_box."""
    target = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)

    prim = obj_test_geo.iterPrims()[0]

    assert houdini_toolbox.inline.api.primitive_bounding_box(prim) == target


def test_destroy_empty_groups():
    """Test houdini_toolbox.inline.api.destroy_empty_groups."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        houdini_toolbox.inline.api.destroy_empty_groups(
            frozen_geo, hou.attribType.Point
        )

    # Global attribute
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.destroy_empty_groups(geo, hou.attribType.Global)

    # Point group
    geo.createPointGroup("empty")

    houdini_toolbox.inline.api.destroy_empty_groups(geo, hou.attribType.Point)

    assert not geo.pointGroups()

    # Prim group
    geo.createPrimGroup("empty")

    houdini_toolbox.inline.api.destroy_empty_groups(geo, hou.attribType.Prim)

    assert not geo.primGroups()


class Test_rename_group:
    """Test houdini_toolbox.inline.api.rename_group."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.pointGroups()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.rename_group(group, "test_group")

    def test_existing_group(self):
        """Test when the target group already exists."""
        # Existing group
        geo = hou.Geometry()
        geo.createPointGroup("foo")
        bar_group = geo.createPointGroup("bar")

        result = houdini_toolbox.inline.api.rename_group(bar_group, "foo")
        assert result is None

    def test_point_group(self, obj_test_geo_copy):
        """Test renaming a point group."""
        group = obj_test_geo_copy.pointGroups()[0]

        result = houdini_toolbox.inline.api.rename_group(group, "test_group")

        assert result is not None
        assert result.name() == "test_group"

        # Same name.
        group = obj_test_geo_copy.pointGroups()[0]
        name = group.name()

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.rename_group(group, name)

    def test_prim_group(self, obj_test_geo_copy):
        """Test renaming a prim group."""
        group = obj_test_geo_copy.primGroups()[0]

        result = houdini_toolbox.inline.api.rename_group(group, "test_group")

        assert result is not None
        assert result.name() == "test_group"

        # Same name
        group = obj_test_geo_copy.primGroups()[0]
        name = group.name()

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.rename_group(group, name)

    def test_edge_group(self, obj_test_geo_copy):
        """Test renaming an edge group."""
        group = obj_test_geo_copy.edgeGroups()[0]

        result = houdini_toolbox.inline.api.rename_group(group, "test_group")

        assert result is not None
        assert result.name() == "test_group"

        # Same name
        group = obj_test_geo_copy.edgeGroups()[0]
        name = group.name()

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.rename_group(group, name)


class Test_group_bounding_box:
    """Test houdini_toolbox.inline.api.group_bounding_box."""

    def test_point_group(self, obj_test_geo):
        """Test getting the bounding box from a point group."""
        target = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        group = obj_test_geo.pointGroups()[0]
        bbox = houdini_toolbox.inline.api.group_bounding_box(group)

        assert bbox == target

    def test_prim_group(self, obj_test_geo):
        """Test getting the bounding box from a prim group."""
        target = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        group = obj_test_geo.primGroups()[0]
        bbox = houdini_toolbox.inline.api.group_bounding_box(group)

        assert bbox == target

    def test_edge_group(self, obj_test_geo):
        """Test getting the bounding box from an edge group."""
        target = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

        group = obj_test_geo.edgeGroups()[0]
        bbox = houdini_toolbox.inline.api.group_bounding_box(group)

        assert bbox == target


class Test_group_size:
    """Test houdini_toolbox.inline.api.group_size."""

    def test_point_group(self, obj_test_geo):
        """Test getting the size of a point group."""
        group = obj_test_geo.pointGroups()[0]

        assert houdini_toolbox.inline.api.group_size(group) == 12

    def test_prim_group(self, obj_test_geo):
        """Test getting the size of a prim group."""
        group = obj_test_geo.primGroups()[0]

        assert houdini_toolbox.inline.api.group_size(group) == 39

    def test_edge_group(self, obj_test_geo):
        """Test getting the size of an edge group."""
        group = obj_test_geo.edgeGroups()[0]

        assert houdini_toolbox.inline.api.group_size(group) == 52


class Test_toggle_group_entries:
    """Test houdini_toolbox.inline.api.toggle_group_entries."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.pointGroups()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.toggle_group_entries(group)

    def test_point_group(self, obj_test_geo_copy):
        """Test toggling point group entries."""
        values = obj_test_geo_copy.globPoints(
            " ".join([str(val) for val in range(1, 100, 2)])
        )

        group = obj_test_geo_copy.pointGroups()[0]
        houdini_toolbox.inline.api.toggle_group_entries(group)

        assert group.points() == values

    def test_prim_group(self, obj_test_geo_copy):
        """Test toggling prim group entries."""
        values = obj_test_geo_copy.globPrims(
            " ".join([str(val) for val in range(0, 100, 2)])
        )

        group = obj_test_geo_copy.primGroups()[0]
        houdini_toolbox.inline.api.toggle_group_entries(group)

        assert group.prims() == values

    def test_edge_group(self, obj_test_geo_copy):
        """Test toggling edge group entries."""
        group = obj_test_geo_copy.edgeGroups()[0]
        houdini_toolbox.inline.api.toggle_group_entries(group)

        assert len(group.edges()) == 20


class Test_copy_group:
    """Test houdini_toolbox.inline.api.copy_group."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.pointGroups()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.copy_group(group, "new_group")

    def test_point_group(self, obj_test_geo_copy):
        """Test copying a point group."""
        group = obj_test_geo_copy.pointGroups()[0]

        new_group = houdini_toolbox.inline.api.copy_group(group, "new_group")

        assert group.points() == new_group.points()

    def test_point_group__same_name(self, obj_test_geo_copy):
        """Test copying a point group to the same name."""
        group = obj_test_geo_copy.pointGroups()[0]

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.copy_group(group, group.name())

    def test_point_group__exists(self, obj_test_geo_copy):
        """Test copying a point group to a group name which already exists."""
        group = obj_test_geo_copy.pointGroups()[-1]

        other_group = obj_test_geo_copy.pointGroups()[0]

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.copy_group(group, other_group.name())

    def test_prim_group(self, obj_test_geo_copy):
        """Test copying a prim group."""
        group = obj_test_geo_copy.primGroups()[0]

        new_group = houdini_toolbox.inline.api.copy_group(group, "new_group")

        assert group.prims() == new_group.prims()

    def test_prim_group__same_name(self, obj_test_geo_copy):
        """Test copying a prim group to the same name."""
        group = obj_test_geo_copy.primGroups()[0]

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.copy_group(group, group.name())

    def test_prim_group__exists(self, obj_test_geo_copy):
        """Test copying a prim group to a group name which already exists."""
        group = obj_test_geo_copy.primGroups()[-1]

        other_group = obj_test_geo_copy.primGroups()[0]

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.copy_group(group, other_group.name())


class Test_set_group_string_attribute:
    """Test houdini_toolbox.inline.api.set_group_string_attribute."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.pointGroups()[0]
        attribute = obj_test_geo.findPointAttrib("point_not_string")

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.set_group_string_attribute(
                group, attribute, "value"
            )

    def test_not_string_attribute(self, obj_test_geo_copy):
        """Test trying to set a non-string attribute."""
        group = obj_test_geo_copy.pointGroups()[0]
        attribute = obj_test_geo_copy.findPointAttrib("point_not_string")

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.set_group_string_attribute(
                group, attribute, "value"
            )

    def test_point_group(self, obj_test_geo_copy):
        """Test setting a point group string attribute."""
        group = obj_test_geo_copy.pointGroups()[0]
        attribute = obj_test_geo_copy.findPointAttrib("point_attrib")

        houdini_toolbox.inline.api.set_group_string_attribute(group, attribute, "value")

        expected = tuple(["value"] * 6 + ["default"] * 3)

        assert obj_test_geo_copy.pointStringAttribValues("point_attrib") == expected

    def test_prim_group(self, obj_test_geo_copy):
        """Test setting a prim group string attribute."""
        group = obj_test_geo_copy.primGroups()[0]
        attribute = obj_test_geo_copy.findPrimAttrib("prim_attrib")

        houdini_toolbox.inline.api.set_group_string_attribute(group, attribute, "value")

        expected = tuple(["value"] * 3 + ["default"])

        assert obj_test_geo_copy.primStringAttribValues("prim_attrib") == expected


class Test_groups_share_elements:
    """Test houdini_toolbox.inline.api.groups_share_elements."""

    def test_different_details(self, obj_test_geo):
        """Test when two groups are in different details."""
        group1 = obj_test_geo.pointGroups()[0]

        temp_geo = hou.Geometry()
        group2 = temp_geo.createPointGroup("temp")

        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.groups_share_elements(group1, group2)

    def test_different_types(self, obj_test_geo):
        """Test when two groups are different element types."""
        group1 = obj_test_geo.pointGroups()[0]
        group2 = obj_test_geo.primGroups()[0]

        with pytest.raises(TypeError):
            houdini_toolbox.inline.api.groups_share_elements(group1, group2)

    def test_point_groups_share_elements(self, obj_test_geo):
        """Test when two point groups share elements."""
        group1 = obj_test_geo.findPointGroup("point_group_every_other")
        group2 = obj_test_geo.findPointGroup("point_group_all")

        assert houdini_toolbox.inline.api.groups_share_elements(group1, group2)

    def test_point_groups_no_shared_elements(self, obj_test_geo):
        """Test when two point groups do not share elements."""
        group1 = obj_test_geo.findPointGroup("point_group_every_other")
        group2 = obj_test_geo.findPointGroup("point_group_empty")

        assert not houdini_toolbox.inline.api.groups_share_elements(group1, group2)

    def test_prim_groups_share_elements(self, obj_test_geo):
        """Test when two prim groups share elements."""
        group1 = obj_test_geo.findPrimGroup("prim_group_every_other")
        group2 = obj_test_geo.findPrimGroup("prim_group_all")

        assert houdini_toolbox.inline.api.groups_share_elements(group1, group2)

    def test_prim_groups_no_shared_elements(self, obj_test_geo):
        """Test when two prim groups do not share elements."""
        group1 = obj_test_geo.findPrimGroup("prim_group_every_other")
        group2 = obj_test_geo.findPrimGroup("prim_group_empty")

        assert not houdini_toolbox.inline.api.groups_share_elements(group1, group2)


class Test_convert_prim_to_point_group:
    """Test houdini_toolbox.inline.api.convert_prim_to_point_group."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.primGroups()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.convert_prim_to_point_group(group)

    def test_same_name(self, obj_test_geo_copy):
        """Test converting to a group with the same name as the source and
        deleting the source group.

        """
        group = obj_test_geo_copy.primGroups()[0]

        new_group = houdini_toolbox.inline.api.convert_prim_to_point_group(group)

        assert len(new_group.iterPoints()) == 12

        # Check source group was deleted.
        assert not obj_test_geo_copy.primGroups()

    def test_new_name(self, obj_test_geo_copy):
        """Test converting to a group with a different name as the source and
        deleting the source group.

        """
        group = obj_test_geo_copy.primGroups()[0]

        new_group = houdini_toolbox.inline.api.convert_prim_to_point_group(
            group, "new_group"
        )

        assert new_group.name() == "new_group"

        # Check source group was deleted.
        assert not obj_test_geo_copy.primGroups()

    def test_same_name_no_destroy(self, obj_test_geo_copy):
        """Test converting to a group with the same name as the source and
        not deleting the source group.

        """
        group = obj_test_geo_copy.primGroups()[0]

        houdini_toolbox.inline.api.convert_prim_to_point_group(group, destroy=False)

        # Check source group wasn't deleted.
        assert len(obj_test_geo_copy.primGroups()) == 1

    def test_target_name_already_exists(self, obj_test_geo_copy):
        """Test converting when the target name exists."""
        group = obj_test_geo_copy.primGroups()[0]

        obj_test_geo_copy.createPointGroup(group.name())

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.convert_prim_to_point_group(group, group.name())


class Test_convert_point_to_prim_group:
    """Test houdini_toolbox.inline.api.convert_point_to_prim_group."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        group = obj_test_geo.pointGroups()[0]

        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.convert_point_to_prim_group(group)

    def test_same_name(self, obj_test_geo_copy):
        """Test converting to a group with the same name as the source and
        deleting the source group.

        """
        group = obj_test_geo_copy.pointGroups()[0]

        new_group = houdini_toolbox.inline.api.convert_point_to_prim_group(group)

        assert len(new_group.iterPrims()) == 5

        # Check source group was deleted.
        assert not obj_test_geo_copy.pointGroups()

    def test_new_name(self, obj_test_geo_copy):
        """Test converting to a group with a different name as the source and
        deleting the source group.

        """
        group = obj_test_geo_copy.pointGroups()[0]

        new_group = houdini_toolbox.inline.api.convert_point_to_prim_group(
            group, "new_group"
        )

        assert new_group.name() == "new_group"

    def test_same_name_no_destroy(self, obj_test_geo_copy):
        """Test converting to a group with the same name as the source and
        not deleting the source group.

        """
        group = obj_test_geo_copy.pointGroups()[0]

        houdini_toolbox.inline.api.convert_point_to_prim_group(group, destroy=False)

        # Check source group wasn't deleted.
        assert len(obj_test_geo_copy.pointGroups()) == 1

    def test_target_name_already_exists(self, obj_test_geo_copy):
        """Test converting when the target name exists."""
        group = obj_test_geo_copy.pointGroups()[0]

        obj_test_geo_copy.createPrimGroup(group.name())

        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.convert_point_to_prim_group(group, group.name())


# =========================================================================
# UNGROUPED POINTS
# =========================================================================


class Test_geometry_has_ungrouped_points:
    """Test houdini_toolbox.inline.api.geometry_has_ungrouped_points."""

    def test_has_ungrouped(self):
        """Test geometry which has ungrouped points."""
        geo = hou.Geometry()
        geo.createPoint()

        assert houdini_toolbox.inline.api.geometry_has_ungrouped_points(geo)

    def test_no_ungrouped(self, obj_test_geo):
        """Test geometry which does not have ungrouped points."""
        assert not houdini_toolbox.inline.api.geometry_has_ungrouped_points(
            obj_test_geo
        )


class Test_group_ungrouped_points:
    """Test houdini_toolbox.inline.api.group_ungrouped_points."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.group_ungrouped_points(obj_test_geo, "ungrouped")

    def test_empty_name(self, obj_test_geo_copy):
        """Test when the target group name is empty."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.group_ungrouped_points(obj_test_geo_copy, "")

    def test_existing_name(self, obj_test_geo_copy):
        """Test when the target group name already exists."""
        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.group_ungrouped_points(
                obj_test_geo_copy, "group1"
            )

    def test_ungrouped(self, obj_test_geo_copy):
        """Test when there are ungrouped points to group."""
        group = houdini_toolbox.inline.api.group_ungrouped_points(
            obj_test_geo_copy, "ungrouped"
        )

        assert len(group.points()) == 10

    def test_no_ungrouped(self, obj_test_geo_copy):
        """Test when there are no ungrouped points to group."""
        group = houdini_toolbox.inline.api.group_ungrouped_points(
            obj_test_geo_copy, "ungrouped"
        )

        assert group is None


# =========================================================================
# UNGROUPED PRIMS
# =========================================================================


class Test_has_ungrouped_prims:
    """Test houdini_toolbox.inline.api.geometry_has_ungrouped_prims."""

    def test_has_ungrouped(self):
        """Test geometry which has ungrouped prims."""
        geo = hou.Geometry()
        geo.createPolygon()

        assert houdini_toolbox.inline.api.geometry_has_ungrouped_prims(geo)

    def test_no_ungrouped(self, obj_test_geo):
        """Test geometry which does not have ungrouped prims."""
        assert not houdini_toolbox.inline.api.geometry_has_ungrouped_prims(obj_test_geo)


class Test_group_ungrouped_prims:
    """Test houdini_toolbox.inline.api.group_ungrouped_prims."""

    def test_read_only(self, obj_test_geo):
        """Test when the geometry is read only."""
        with pytest.raises(hou.GeometryPermissionError):
            houdini_toolbox.inline.api.group_ungrouped_prims(obj_test_geo, "ungrouped")

    def test_empty_name(self, obj_test_geo_copy):
        """Test when the target group name is empty."""
        with pytest.raises(ValueError):
            houdini_toolbox.inline.api.group_ungrouped_prims(obj_test_geo_copy, "")

    def test_existing_name(self, obj_test_geo_copy):
        """Test when the target group name already exists."""
        with pytest.raises(hou.OperationFailed):
            houdini_toolbox.inline.api.group_ungrouped_prims(
                obj_test_geo_copy, "group1"
            )

    def test_ungrouped(self, obj_test_geo_copy):
        """Test when there are ungrouped prims to group."""
        group = houdini_toolbox.inline.api.group_ungrouped_prims(
            obj_test_geo_copy, "ungrouped"
        )

        assert len(group.iterPrims()) == 3

    def test_no_ungrouped(self, obj_test_geo_copy):
        """Test when there are not ungrouped prims to group."""
        group = houdini_toolbox.inline.api.group_ungrouped_prims(
            obj_test_geo_copy, "ungrouped"
        )

        assert group is None


@pytest.mark.parametrize(
    "bbox, expected",
    [
        (hou.BoundingBox(-1, -1, -1, 1, 1, 1), True),  # Inside
        (hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5), False),  # Not inside
    ],
)
def test_bounding_box_is_inside(bbox, expected):
    """Test houdini_toolbox.inline.api.bounding_box_is_inside."""
    test_bbox = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)

    assert (
        houdini_toolbox.inline.api.bounding_box_is_inside(test_bbox, bbox) == expected
    )


@pytest.mark.parametrize(
    "bbox, expected",
    [
        (hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5), True),  # Intersects
        (
            hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1),
            False,
        ),  # Doesn't intersect
    ],
)
def test_bounding_boxes_intersect(bbox, expected):
    """Test houdini_toolbox.inline.api.bounding_boxes_intersect."""
    test_bbox = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert (
        houdini_toolbox.inline.api.bounding_boxes_intersect(test_bbox, bbox) == expected
    )


def test_compute_bounding_box_intersection():
    """Test houdini_toolbox.inline.api.compute_bounding_box_intersection."""
    bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert houdini_toolbox.inline.api.compute_bounding_box_intersection(bbox1, bbox2)

    assert bbox1.minvec() == hou.Vector3()
    assert bbox1.maxvec() == hou.Vector3(0.5, 0.5, 0.5)

    # Unable to compute interaction.
    bbox3 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)

    assert not houdini_toolbox.inline.api.compute_bounding_box_intersection(
        bbox3, bbox2
    )


def test_expand_bounding_box():
    """Test houdini_toolbox.inline.api.expand_bounding_box."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    houdini_toolbox.inline.api.expand_bounding_box(bbox, 1, 1, 1)

    assert bbox.minvec() == hou.Vector3(-2, -2.75, -4)
    assert bbox.maxvec() == hou.Vector3(2, 2.75, 4)


def test_add_to_bounding_box_min():
    """Test houdini_toolbox.inline.api.add_to_bounding_box_min."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    houdini_toolbox.inline.api.add_to_bounding_box_min(bbox, hou.Vector3(1, 0.25, 1))

    assert bbox.minvec() == hou.Vector3(0, -1.5, -2)


def test_add_to_bounding_box_max():
    """Test houdini_toolbox.inline.api.add_to_bounding_box_max."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    houdini_toolbox.inline.api.add_to_bounding_box_max(bbox, hou.Vector3(2, 0.25, 1))

    assert bbox.maxvec() == hou.Vector3(3, 2, 4)


def test_bounding_box_area():
    """Test houdini_toolbox.inline.api.bounding_box_area."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert houdini_toolbox.inline.api.bounding_box_area(bbox) == 80


def test_bounding_box_volume():
    """Test houdini_toolbox.inline.api.bounding_box_volume."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert houdini_toolbox.inline.api.bounding_box_volume(bbox) == 42


# =========================================================================
# PARMS
# =========================================================================


def test_is_parm_tuple_vector():
    """Test houdini_toolbox.inline.api.is_parm_tuple_vector."""
    node = OBJ.node("test_is_vector/node")
    parm = node.parmTuple("vec")

    assert houdini_toolbox.inline.api.is_parm_tuple_vector(parm)

    # Not a vector parameter.
    parm = node.parmTuple("not_vec")

    assert not houdini_toolbox.inline.api.is_parm_tuple_vector(parm)


def test_eval_parm_tuple_as_vector():
    """Test houdini_toolbox.inline.api.eval_parm_tuple_as_vector."""
    node = OBJ.node("test_eval_as_vector/node")
    parm = node.parmTuple("vec2")

    assert houdini_toolbox.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector2(
        1, 2
    )

    parm = node.parmTuple("vec3")

    assert houdini_toolbox.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector3(
        3, 4, 5
    )

    parm = node.parmTuple("vec4")

    assert houdini_toolbox.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector4(
        6, 7, 8, 9
    )

    parm = node.parmTuple("not_vec")

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.eval_parm_tuple_as_vector(parm)


def test_is_parm_tuple_color():
    """Test houdini_toolbox.inline.api.is_parm_tuple_color."""
    node = OBJ.node("test_is_color/node")
    parm = node.parmTuple("color")

    assert houdini_toolbox.inline.api.is_parm_tuple_color(parm)

    # Not a color.
    parm = node.parmTuple("not_color")

    assert not houdini_toolbox.inline.api.is_parm_tuple_color(parm)


def test_eval_parm_tuple_as_color():
    """Test houdini_toolbox.inline.api.eval_parm_tuple_as_color."""
    node = OBJ.node("test_eval_as_color/node")
    parm = node.parmTuple("color")

    assert houdini_toolbox.inline.api.eval_parm_tuple_as_color(parm) == hou.Color(
        0, 0.5, 0.5
    )

    # Not a color.
    parm = node.parmTuple("not_color")

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.eval_parm_tuple_as_color(parm)


def test_eval_parm_as_strip():
    """Test houdini_toolbox.inline.api.eval_parm_as_strip."""
    node = OBJ.node("test_eval_as_strip/node")

    parm = node.parm("cacheinput")

    with pytest.raises(TypeError):
        houdini_toolbox.inline.api.eval_parm_as_strip(parm)

    parm = node.parm("strip_normal")

    target = (False, True, False, False)

    assert houdini_toolbox.inline.api.eval_parm_as_strip(parm) == target

    # Toggle strip
    parm = node.parm("strip_toggle")

    target = (True, False, True, True)

    assert houdini_toolbox.inline.api.eval_parm_as_strip(parm) == target


def test_eval_parm_strip_as_string():
    """Test houdini_toolbox.inline.api.eval_parm_strip_as_string."""
    node = OBJ.node("test_eval_as_strip/node")
    parm = node.parm("strip_normal")

    target = ("bar",)

    assert houdini_toolbox.inline.api.eval_parm_strip_as_string(parm) == target

    # Toggle strip.
    parm = node.parm("strip_toggle")

    target = ("foo", "hello", "world")

    assert houdini_toolbox.inline.api.eval_parm_strip_as_string(parm) == target


# =========================================================================
# MULTIPARMS
# =========================================================================


def test_is_parm_multiparm():
    """Test houdini_toolbox.inline.api.is_parm_multiparm."""
    node = OBJ.node("test_is_multiparm/object_merge")
    parm = node.parm("numobj")

    assert houdini_toolbox.inline.api.is_parm_multiparm(parm)

    parm_tuple = node.parmTuple("numobj")
    assert houdini_toolbox.inline.api.is_parm_multiparm(parm_tuple)

    parm = node.parm("objpath1")
    assert not houdini_toolbox.inline.api.is_parm_multiparm(parm)

    parm_tuple = node.parmTuple("objpath1")
    assert not houdini_toolbox.inline.api.is_parm_multiparm(parm_tuple)

    # Check against all different FolderSet type folders.
    for folder_name in (
        "folder_tabs",
        "folder_collapsible",
        "folder_simple",
        "folder_radio",
    ):
        parm = node.parm(folder_name)
        assert not houdini_toolbox.inline.api.is_parm_multiparm(parm)

    # Check against additional multiparm types.
    for folder_name in ("multi_scroll", "multi_tab"):
        parm = node.parm(folder_name)
        assert houdini_toolbox.inline.api.is_parm_multiparm(parm)

        parm_tuple = node.parmTuple(folder_name)
        assert houdini_toolbox.inline.api.is_parm_multiparm(parm_tuple)


def test_get_multiparm_instance_indices():
    """Test houdini_toolbox.inline.api.get_multiparm_instance_index."""
    node = OBJ.node("test_get_multiparm_instance_indices/null")
    parm = node.parm("vecparm0x")

    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm) == (0,)

    parm_tuple = node.parmTuple("vecparm0")

    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm_tuple) == (0,)

    parm_tuple = node.parmTuple("vecparm1")
    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm_tuple) == (1,)

    parm_tuple = node.parmTuple("inner0")

    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm_tuple) == (0,)

    parm = node.parm("leaf0_1")

    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm) == (0, 1)
    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm, True) == (
        0,
        0,
    )

    parm = node.parm("leaf1_5")

    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm) == (1, 5)
    assert houdini_toolbox.inline.api.get_multiparm_instance_indices(parm, True) == (
        1,
        4,
    )

    parm = node.parm("base")

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.get_multiparm_instance_indices(parm)

    parm_tuple = node.parmTuple("base")

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.get_multiparm_instance_indices(parm_tuple)


def test_get_multiparm_siblings():
    """Test houdini_toolbox.inline.api.get_multiparm_siblings."""
    node = OBJ.node("test_get_multiparm_siblings/null")

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.get_multiparm_siblings(node.parm("base"))

    parm = node.parm("stringparm0")

    expected = {
        "inner_multi#": node.parm("inner_multi0"),
        "vecparm#": node.parmTuple("vecparm0"),
        "simple_intparm#": node.parm("simple_intparm0"),
        "tab_intparm1#": node.parm("tab_intparm10"),
        "collapse_intparm#": node.parm("collapse_intparm0"),
        "tab_intparm2#": node.parm("tab_intparm20"),
    }

    assert houdini_toolbox.inline.api.get_multiparm_siblings(parm) == expected

    parm_tuple = node.parmTuple("vecparm0")

    expected = {
        "inner_multi#": node.parm("inner_multi0"),
        "stringparm#": node.parm("stringparm0"),
        "simple_intparm#": node.parm("simple_intparm0"),
        "tab_intparm1#": node.parm("tab_intparm10"),
        "collapse_intparm#": node.parm("collapse_intparm0"),
        "tab_intparm2#": node.parm("tab_intparm20"),
    }

    assert houdini_toolbox.inline.api.get_multiparm_siblings(parm_tuple) == expected


def test_resolve_multiparm_tokens():
    """Test houdini_toolbox.inline.api.resolve_multiparm_tokens."""
    assert houdini_toolbox.inline.api.resolve_multiparm_tokens("test#", 3) == "test3"
    assert houdini_toolbox.inline.api.resolve_multiparm_tokens("test#", (4,)) == "test4"
    assert (
        houdini_toolbox.inline.api.resolve_multiparm_tokens(
            "test#",
            [
                5,
            ],
        )
        == "test5"
    )

    assert (
        houdini_toolbox.inline.api.resolve_multiparm_tokens("test#_#_#", [1, 2, 3])
        == "test1_2_3"
    )

    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.resolve_multiparm_tokens(
            "test#_#",
            [
                5,
            ],
        )


def test_get_multiparm_template_name():
    """Test houdini_toolbox.inline.api.get_multiparm_template_name."""
    node = OBJ.node("test_get_multiparm_template_name/null")

    parm = node.parm("base")
    assert houdini_toolbox.inline.api.get_multiparm_template_name(parm) is None

    parm = node.parm("inner0")
    assert houdini_toolbox.inline.api.get_multiparm_template_name(parm) == "inner#"

    parm_tuple = node.parmTuple("vecparm0")
    assert (
        houdini_toolbox.inline.api.get_multiparm_template_name(parm_tuple) == "vecparm#"
    )

    parm = node.parm("leaf1_3")
    assert houdini_toolbox.inline.api.get_multiparm_template_name(parm) == "leaf#_#"


def test_eval_multiparm_instance():
    """Test houdini_toolbox.inline.api.eval_multiparm_instance."""
    node = OBJ.node("test_eval_multiparm_instance/null")

    # Test name with no tokens.
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.eval_multiparm_instance(node, "base", 0)

    # Test name which does not exist.
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.eval_multiparm_instance(node, "foo#", 0)

    expected = [
        (1.1, 2.2, 3.3, 4.4),
        1,
        2,
        3,
        10,
        str(hou.intFrame()),
        (5.5, 6.6, 7.7, 8.8),
        5,
        6,
        7,
        8,
        9,
        hou.hipFile.path(),
    ]

    results = []

    for i in range(node.evalParm("base")):
        # Test a float vector parameter.
        results.append(
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "vecparm#", i)
        )

        # Test a bunch of nested int parameters.
        for j in range(
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "inner#", i)
        ):
            results.append(
                houdini_toolbox.inline.api.eval_multiparm_instance(
                    node, "leaf#_#", [i, j]
                )
            )

        # Test a string parameter which will be expanded.
        results.append(
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "string#", i)
        )

    assert results == expected

    results = []

    # Run the same test again but passing True for raw_indices.
    for i in range(node.evalParm("base")):
        # Test a float vector parameter.
        results.append(
            houdini_toolbox.inline.api.eval_multiparm_instance(
                node, "vecparm#", i, True
            )
        )

        # Test a bunch of nested int parameters.
        for j in range(
            1,
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "inner#", i, True)
            + 1,
        ):
            results.append(
                houdini_toolbox.inline.api.eval_multiparm_instance(
                    node, "leaf#_#", [i, j], True
                )
            )

        # Test a string parameter which will be expanded.
        results.append(
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "string#", i, True)
        )

    assert results == expected

    with pytest.raises(IndexError):
        houdini_toolbox.inline.api.eval_multiparm_instance(node, "vecparm#", 10)


def test_unexpanded_string_multiparm_instance():
    """Test houdini_toolbox.inline.api.unexpanded_string_multiparm_instance."""
    node = OBJ.node("test_unexpanded_string_multiparm_instance/null")

    # Test name with no tokens.
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(node, "base", 0)

    # Test name which does not exist.
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(node, "foo#", 0)

    # Test a non-string parm
    with pytest.raises(TypeError):
        houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
            node, "float#", 0
        )

    expected = [
        "$F",
        ("$E", "$C"),
        ("$EYE", "$HOME"),
        "$HIPFILE",
        ("$JOB", "$TEMP"),
        ("$FOO", "$BAR"),
    ]

    results = []

    for i in range(node.evalParm("base")):
        results.append(
            houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
                node, "string#", i
            )
        )

        for j in range(
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "inner#", i)
        ):
            results.append(
                houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
                    node, "nested_string#_#", [i, j]
                )
            )

    assert results == expected

    results = []

    # Run the same test again but passing True for raw_indices.
    for i in range(node.evalParm("base")):
        # Test a float vector parameter.
        results.append(
            houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
                node, "string#", i, True
            )
        )

        # Test a bunch of nested int parameters.
        for j in range(
            1,
            houdini_toolbox.inline.api.eval_multiparm_instance(node, "inner#", i, True)
            + 1,
        ):
            results.append(
                houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
                    node, "nested_string#_#", [i, j], True
                )
            )

    assert results == expected

    with pytest.raises(IndexError):
        houdini_toolbox.inline.api.unexpanded_string_multiparm_instance(
            node, "string#", 10
        )


# =========================================================================
# NODES AND NODE TYPES
# =========================================================================


def test_disconnect_all_outputs():
    """Test houdini_toolbox.inline.api.disconnect_all_inputs."""
    node = OBJ.node("test_disconnect_all_outputs/file")

    houdini_toolbox.inline.api.disconnect_all_outputs(node)

    assert not node.outputs()


def test_disconnect_all_inputs():
    """Test houdini_toolbox.inline.api.disconnect_all_outputs."""
    node = OBJ.node("test_disconnect_all_inputs/merge")

    houdini_toolbox.inline.api.disconnect_all_inputs(node)

    assert not node.inputs()


def test_node_is_contained_by():
    """Test houdini_toolbox.inline.api.node_is_contained_by."""
    node = OBJ.node("test_is_contained_by")

    box = node.node("subnet/box")

    assert houdini_toolbox.inline.api.node_is_contained_by(box, node)
    assert not houdini_toolbox.inline.api.node_is_contained_by(node, hou.node("/shop"))


def test_author_name():
    """Test houdini_toolbox.inline.api.node_author_name."""
    node = OBJ.node("test_author_name")

    assert houdini_toolbox.inline.api.node_author_name(node) == "grahamt"


def test_is_node_type_python():
    """Test houdini_toolbox.inline.api.is_node_type_python."""
    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")
    assert houdini_toolbox.inline.api.is_node_type_python(node_type)

    # Not python
    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "file")
    assert not houdini_toolbox.inline.api.is_node_type_python(node_type)


def test_is_node_type_subnet():
    """Test houdini_toolbox.inline.api.is_node_type_subnet."""
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "subnet")
    assert houdini_toolbox.inline.api.is_node_type_subnet(node_type)

    # Not a subnet.
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
    assert not houdini_toolbox.inline.api.is_node_type_subnet(node_type)


# =========================================================================
# VECTORS AND MATRICES
# =========================================================================


def test_vector_component_along():
    """Test houdini_toolbox.inline.api.vector_component_along."""
    vec = hou.Vector3(1, 2, 3)

    assert (
        houdini_toolbox.inline.api.vector_component_along(vec, hou.Vector3(0, 0, 15))
        == 3.0
    )


def test_vector_project_along():
    """Test houdini_toolbox.inline.api.vector_project_along."""
    vec = hou.Vector3(-1.3, 0.5, 7.6)

    # Test zero-length vector
    with pytest.raises(ValueError):
        houdini_toolbox.inline.api.vector_project_along(vec, hou.Vector3())

    projection = houdini_toolbox.inline.api.vector_project_along(
        vec, hou.Vector3(2.87, 3.1, -0.5)
    )

    result = hou.Vector3(-0.948531, -1.02455, 0.165249)

    assert projection.isAlmostEqual(result)


@pytest.mark.parametrize(
    "vec, expected",
    [
        ((), False),
        (hou.Vector2(1, 0), False),
        (hou.Vector2(float("nan"), 1), True),
        (hou.Vector3(6.5, 1, float("nan")), True),
        (hou.Vector4(-4.0, 5, -0, float("nan")), True),
    ],
)
def test_vector_contains_nans(vec, expected):
    """Test houdini_toolbox.inline.api.vector_contains_nans."""
    result = houdini_toolbox.inline.api.vector_contains_nans(vec)
    assert result == expected


def test_vector_compute_dual():
    """Test houdini_toolbox.inline.api.vector_compute_dual."""
    target = hou.Matrix3()
    target.setTo(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

    vec = hou.Vector3(1, 2, 3)

    assert houdini_toolbox.inline.api.vector_compute_dual(vec) == target


def test_matrix_is_identity():
    """Test houdini_toolbox.inline.api.matrix_is_identity."""
    # Matrix 3
    mat3 = hou.Matrix3()
    mat3.setToIdentity()

    assert houdini_toolbox.inline.api.matrix_is_identity(mat3)

    # Not the identity matrix.
    mat3 = hou.Matrix3()
    assert not houdini_toolbox.inline.api.matrix_is_identity(mat3)

    # Matrix4
    mat4 = hou.Matrix4()
    mat4.setToIdentity()

    assert houdini_toolbox.inline.api.matrix_is_identity(mat4)

    # Not the identity matrix.
    mat4 = hou.Matrix4()
    assert not houdini_toolbox.inline.api.matrix_is_identity(mat4)


def test_matrix_set_translates():
    """Test houdini_toolbox.inline.api.matrix_set_translates."""
    translates = hou.Vector3(1, 2, 3)
    identity = hou.hmath.identityTransform()
    houdini_toolbox.inline.api.matrix_set_translates(identity, translates)

    assert identity.extractTranslates() == translates


def test_build_lookat_matrix():
    """Test houdini_toolbox.inline.api.build_lookat_matrix."""
    target = hou.Matrix3()

    target.setTo(
        (
            (0.70710678118654746, -0.0, 0.70710678118654746),
            (0.0, 1.0, 0.0),
            (-0.70710678118654746, 0.0, 0.70710678118654746),
        )
    )

    mat = houdini_toolbox.inline.api.build_lookat_matrix(
        hou.Vector3(0, 0, 1), hou.Vector3(1, 0, 0), hou.Vector3(0, 1, 0)
    )

    assert mat == target


def test_get_oriented_point_transform():
    """Test houdini_toolbox.inline.api.get_oriented_point_transform."""
    # Test against a primitive with no transform.
    geo = OBJ.node("test_get_oriented_point_transform/RAW").geometry()
    pt = geo.points()[0]

    with pytest.raises(hou.OperationFailed):
        houdini_toolbox.inline.api.get_oriented_point_transform(pt)

    # Primitive with proper transform.
    target = hou.Matrix4(
        (
            (0.6819891929626465, -0.7313622236251831, 0.0, 0.0),
            (0.48333778977394104, 0.4507084786891937, -0.7504974603652954, 0.0),
            (0.5488855242729187, 0.5118311643600464, 0.660873293876648, 0.0),
            (0.3173518180847168, 0.38005995750427246, -0.6276679039001465, 1.0),
        )
    )

    geo = OBJ.node("test_get_oriented_point_transform/XFORMED").geometry()
    pt = geo.points()[0]

    result = houdini_toolbox.inline.api.get_oriented_point_transform(pt)

    assert result == target

    # Just a lone point.

    target = hou.Matrix4(
        (
            (-0.42511632340174754, 0.8177546905539287, -0.38801208441803603, 0.0),
            (-0.3819913447800112, 0.2265424934082094, 0.895969369562124, 0.0),
            (0.8205843796286518, 0.5291084621865726, 0.21606830205289468, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
    )

    geo = OBJ.node("test_get_oriented_point_transform/SINGLE_POINT").geometry()
    pt = geo.points()[0]

    result = houdini_toolbox.inline.api.get_oriented_point_transform(pt)

    assert result == target


def test_point_instance_transform(obj_test_geo):
    """Test houdini_toolbox.inline.api.point_instance_transform."""
    target = hou.Matrix4(
        (
            (-0.42511632340174754, 0.8177546905539287, -0.38801208441803603, 0.0),
            (-0.3819913447800112, 0.2265424934082094, 0.895969369562124, 0.0),
            (0.8205843796286518, 0.5291084621865726, 0.21606830205289468, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
    )

    pt = obj_test_geo.points()[0]

    result = houdini_toolbox.inline.api.point_instance_transform(pt)

    assert result == target


def test_build_instance_matrix():
    """Test houdini_toolbox.inline.api.build_instance_matrix."""
    target = hou.Matrix4(
        (
            (1.0606601717798214, -1.0606601717798214, 0.0, 0.0),
            (0.61237243569579436, 0.61237243569579436, -1.2247448713915889, 0.0),
            (0.86602540378443882, 0.86602540378443882, 0.86602540378443882, 0.0),
            (-1.0, 2.0, 4.0, 1.0),
        )
    )

    mat = houdini_toolbox.inline.api.build_instance_matrix(
        hou.Vector3(-1, 2, 4),
        hou.Vector3(1, 1, 1),
        pscale=1.5,
        up_vector=hou.Vector3(1, 1, -1),
    )

    assert mat == target

    target = hou.Matrix4(
        (
            (0.4999999701976776, -1.0000000298023224, -1.0000000298023224, 0.0),
            (-1.0000000298023224, 0.4999999701976776, -1.0000000298023224, 0.0),
            (-1.0000000298023224, -1.0000000298023224, 0.4999999701976776, 0.0),
            (-1.0, 2.0, 4.0, 1.0),
        )
    )

    # Test up vector is zero-vector
    mat = houdini_toolbox.inline.api.build_instance_matrix(
        hou.Vector3(-1, 2, 4),
        hou.Vector3(1, 1, 1),
        pscale=1.5,
        up_vector=hou.Vector3(),
    )

    assert mat == target

    # By orient
    target = hou.Matrix4(
        (
            (0.33212996389891691, 0.3465703971119134, -0.87725631768953083, 0.0),
            (-0.53068592057761732, 0.83754512635379064, 0.1299638989169675, 0.0),
            (0.77978339350180514, 0.42238267148014441, 0.46209386281588438, 0.0),
            (-1.0, 2.0, 4.0, 1.0),
        )
    )

    mat = houdini_toolbox.inline.api.build_instance_matrix(
        hou.Vector3(-1, 2, 4), orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
    )

    assert mat == target


# =========================================================================
# DIGITAL ASSETS
# =========================================================================


@pytest.mark.parametrize(
    "node_name, expected_node",
    [
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ],
)
def test_get_node_message_nodes(node_name, expected_node):
    """Test houdini_toolbox.inline.api.get_node_message_nodes."""
    node = OBJ.node(f"test_message_nodes/{node_name}")

    if expected_node is not None:
        target = (node.node(expected_node),)

    else:
        target = ()

    assert houdini_toolbox.inline.api.get_node_message_nodes(node) == target


@pytest.mark.parametrize(
    "node_name, expected_node",
    [
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ],
)
def test_get_node_editable_nodes(node_name, expected_node):
    """Test houdini_toolbox.inline.api.get_node_editable_nodes."""
    node = OBJ.node(f"test_message_nodes/{node_name}")

    if expected_node is not None:
        target = (node.node(expected_node),)

    else:
        target = ()

    assert houdini_toolbox.inline.api.get_node_editable_nodes(node) == target


@pytest.mark.parametrize(
    "node_name, expected_node",
    [
        ("valid", "d/s"),
        ("no_message_nodes", None),
        ("not_otl", None),
    ],
)
def test_get_node_dive_target(node_name, expected_node):
    """Test houdini_toolbox.inline.api.get_node_dive_target."""
    node = OBJ.node(f"test_message_nodes/{node_name}")

    if expected_node is not None:
        target = node.node(expected_node)

    else:
        target = None

    assert houdini_toolbox.inline.api.get_node_dive_target(node) == target


@pytest.mark.parametrize(
    "node_name, expected_node",
    [
        ("test_representative_node", "stereo_camera"),
        ("test_representative_node/left_camera", None),
        ("test_representative_node/visualization_root", None),
        ("test_message_nodes/valid", None),
    ],
)
def test_get_node_representative_node(node_name, expected_node):
    """Test houdini_toolbox.inline.api.get_node_representative_node."""
    node = OBJ.node(node_name)

    if expected_node is not None:
        target = node.node(expected_node)

    else:
        target = None

    assert houdini_toolbox.inline.api.get_node_representative_node(node) == target


@pytest.mark.parametrize(
    "node_name, expected",
    [
        ("test_is_node_digital_asset/is_digital_asset", True),
        ("test_is_node_digital_asset/not_digital_asset", False),
    ],
)
def test_is_node_digital_asset(node_name, expected):
    """Test houdini_toolbox.inline.api.is_node_digital_asset."""
    node = OBJ.node(node_name)

    assert houdini_toolbox.inline.api.is_node_digital_asset(node) == expected


def test_asset_file_meta_source():
    """Test houdini_toolbox.inline.api.asset_file_meta_source."""
    target = "Scanned Asset Library Directories"

    path = hou.text.expandString("$HH/otls/OPlibSop.hda")

    assert houdini_toolbox.inline.api.asset_file_meta_source(path) == target

    assert houdini_toolbox.inline.api.asset_file_meta_source("/some/fake/pat") is None


def test_get_definition_meta_source():
    """Test houdini_toolbox.inline.api.get_definition_meta_source."""
    target = "Scanned Asset Library Directories"

    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

    assert (
        houdini_toolbox.inline.api.get_definition_meta_source(node_type.definition())
        == target
    )


def test_libraries_in_meta_source():
    """Test houdini_toolbox.inline.api.libraries_in_meta_source."""
    libs = houdini_toolbox.inline.api.libraries_in_meta_source(
        "Scanned Asset Library Directories"
    )
    assert libs


def test_remove_meta_source():
    """Test houdini_toolbox.inline.api.remove_meta_source."""
    subnet = OBJ.createNode("subnet")
    asset = subnet.createDigitalAsset("dummysrcop", "Embedded", "Dummy")
    definition = asset.type().definition()

    asset.destroy()

    assert definition.isInstalled()

    result = houdini_toolbox.inline.api.remove_meta_source("Current HIP File")
    assert result

    assert not definition.isInstalled()


def test_is_dummy_definition():
    """Test houdini_toolbox.inline.api.is_dummy_definition."""
    geo = OBJ.createNode("geo")
    subnet = geo.createNode("subnet")

    # Create a new digital asset.
    asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
    node_type = asset.type()

    # Not a dummy so far.
    assert not houdini_toolbox.inline.api.is_dummy_definition(node_type.definition())

    # Destroy the definition.
    node_type.definition().destroy()

    # Now it's a dummy.
    assert houdini_toolbox.inline.api.is_dummy_definition(node_type.definition())

    # Destroy the instance.
    asset.destroy()

    # Destroy the dummy definition.
    node_type.definition().destroy()
