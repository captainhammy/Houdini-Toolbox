"""Integration tests for ht.geometry.pointcloud."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import object
import os

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.geometry.pointcloud import PointCloud

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def load_test_file():
    """Load the test hip file."""
    hou.hipFile.load(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "test_pointcloud.hipnc"
        ),
        ignore_load_warnings=True,
    )

    yield

    hou.hipFile.clear()


# Need to ensure the hip file gets loaded.
pytestmark = pytest.mark.usefixtures("load_test_file")


# =============================================================================
# TESTS
# =============================================================================


class Test_PointCloud(object):
    """Test ht.geometry.pointcloud.PointCloud."""

    def test_no_points(self):
        """Test trying to create a PointCloud when the geometry has no points."""
        geo = hou.Geometry()

        with pytest.raises(RuntimeError):
            PointCloud(geo)

    def test_find_all_close_points_dist_2__no_results(self):
        """Test find_all_close_points with a max distance of 2, expecting no results."""
        geo = hou.node("/obj/find_all_close_points/test_dist_2__no_results").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_all_close_points(hou.Vector3(1, 0, 0), 2)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_all_close_points_dist_4(self):
        """Test find_all_close_points with a max distance of 4."""
        geo = hou.node("/obj/find_all_close_points/test_dist_4").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_all_close_points(hou.Vector3(1, 0, 0), 4)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_all_close_points_dist_4_in_group(self):
        """Test find_all_close_points with a max distance of 4 using a point mask."""
        geo = hou.node("/obj/find_all_close_points/test_dist_4_in_group").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo, "test_group")

        result = pc.find_all_close_points(hou.Vector3(1, 0, 0), 4)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_bad_points_value(self):
        """Test find_nearest_points when passing an invalid number of points."""
        geo = hou.Geometry()
        geo.createPoint()

        pc = PointCloud(geo)

        with pytest.raises(ValueError):
            pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=0)

    def test_find_nearest_points_dist_4_max_1(self):
        """Test find_nearest_points looking for 1 point within a max distance of 4."""
        geo = hou.node("/obj/find_nearest_points/test_dist_4_max_1").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=1, maxdist=4)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_dist_tiny_max_1(self):
        """Test find_nearest_points looking for 1 point within a very small max distance."""
        geo = hou.node("/obj/find_nearest_points/test_dist_tiny_max_1").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=1, maxdist=0.1)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_dist_4_max_5(self):
        """Test find_nearest_points looking for up to 5 points within a max distance of 4."""
        geo = hou.node("/obj/find_nearest_points/test_dist_4_max_5").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=5, maxdist=4)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_dist_tiny_max_5(self):
        """Test find_nearest_points looking for up to 5 points within a very small max distance."""
        geo = hou.node("/obj/find_nearest_points/test_dist_tiny_max_5").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=5, maxdist=0.1)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_dist_none_max_1(self):
        """Test find_nearest_points looking for 1 point with no max distance."""
        geo = hou.node("/obj/find_nearest_points/test_dist_None_max_1").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=1)

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)

    def test_find_nearest_points_dist_none_max_1000(self):
        """Test find_nearest_points looking for up to 1000 points with no max distance."""
        geo = hou.node("/obj/find_nearest_points/test_dist_None_max_1000").geometry()
        attr = geo.findGlobalAttrib("near")

        pc = PointCloud(geo)

        result = pc.find_nearest_points(hou.Vector3(1, 0, 0), num_points=1000)

        assert len(result) == len(geo.iterPoints())

        assert tuple([pt.number() for pt in result]) == geo.intListAttribValue(attr)
