"""Module to represent geometry as a point cloud in Houdini."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from typing import Optional, Sequence, Tuple

# Third Party Imports
import numpy
from scipy.spatial import KDTree

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================


class PointCloud:
    """A wrapper around scipy.spatial.KDTree to represent point positions.

    :param geometry: The source geometry.
    :param pattern: Optional point selecting pattern.
    :param leaf_size: The tree leaf size.
    :return:

    """

    def __init__(
        self, geometry: hou.Geometry, pattern: Optional[str] = None, leaf_size: int = 10
    ):
        # The source geometry. We need this to be able to glob points.
        self._geometry = geometry

        # Don't create a point map by default.
        self._point_map = None

        if pattern:
            # Get a list of the points we want to build the tree from.
            group_points = geometry.globPoints(pattern)

            # Create a list of all the positions of those points.
            positions = [point.position() for point in group_points]

            # Create a map of the point numbers.  We need to do this because
            # when returning results from queries, it only returns the index
            # numbers. We then use those indexes to get the real point number
            # from the point map.
            self._point_map = [point.number() for point in group_points]

            # Build our data array. Since it was created from a list of
            # hou.Vector3's (tuples) we don't need to reshape.
            data = numpy.array(positions)

            self._num_elements = len(group_points)

        else:
            # Get the point positions as a giant list.
            positions = geometry.pointFloatAttribValues("P")

            # Convert the list of positions to a numpy array and reshape it to
            # represent 3 component entries.
            num_points = len(geometry.iterPoints())
            data = numpy.array(positions).reshape((num_points, 3))

            self._num_elements = num_points

        if self._num_elements == 0:
            raise RuntimeError("Cannot create PointCloud with 0 points")

        # Build the tree from the data.
        self._tree = KDTree(data, leaf_size)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        if self._geometry.sopNode() is not None:
            return "<PointCloud for {}>".format(self._geometry.sopNode().path())

        return "<PointCloud>"

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _get_result_points(self, indexes: Sequence[int]) -> Tuple[hou.Point, ...]:
        """This method converts a list of integers into corresponding hou.Point
        objects belonging to the geometry depending on whether a point map is
        being used.

        :param indexes: A list of point numbers.
        :return: A tuple of points matching the indexes.

        """
        # If we have a point map set up we need to index into that and then
        # convert to string.
        if self._point_map:
            pattern = " ".join([str(self._point_map[index]) for index in indexes])

        # Just convert the indexes to strings.
        else:
            pattern = " ".join([str(index) for index in indexes])

        # Return our matched points.
        return self._geometry.globPoints(pattern)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def find_all_close_points(
        self, position: hou.Vector3, maxdist: float
    ) -> Tuple[hou.Point, ...]:
        """Find all points within the maxdist from the position.

        :param position: A search position.
        :param maxdist: The maximum distance to search.
        :return: A tuple of found points.

        """
        # Convert the position to a compatible ndarray.
        positions = numpy.array([position])

        # Perform a query based on the position and maxdist.
        result = self._tree.query_ball_point(positions, maxdist)

        # Bail out if we got no results since an empty list would be converted to ""
        # and hou.Geometry.globPoints would return all points.
        if not result:
            return tuple()

        # Return any points that are found.
        return self._get_result_points(result[0])

    def find_nearest_points(
        self,
        position: hou.Vector3,
        num_points: int = 1,
        maxdist: Optional[float] = None,
    ) -> Tuple[hou.Point, ...]:
        """Find the closest N points to the position.

        :param position: A search position.
        :param num_points: The maximum number of points to search for.
        :param maxdist: The maximum distance to search.
        :return: A tuple of found points.

        """
        # Return no points if we ask for an invalid number of points.
        if num_points < 1:
            raise ValueError("Must choose 1 or more points")

        # Make sure we aren't querying for more points than we have.
        if num_points > self._num_elements:
            num_points = self._num_elements

        # Convert the position to a compatible ndarray.
        positions = numpy.array([position])

        # Query the tree.
        result = self._tree.query(positions, num_points)

        # Get the list of found indexes.
        indexes = result[1][0]

        # If the maxdist is not None then we specified a maximum distance points
        # can be within.
        if maxdist is not None:
            # Get the distances each match is from the target position.
            distances = result[0][0]

            # Check the type of the distances list.  If it is a numpy array
            # then more than 1 point was found.
            if isinstance(distances, numpy.ndarray):
                # Filter the index list to remove those too far away.
                indexes = [
                    index for dist, index in zip(distances, indexes) if dist < maxdist
                ]

                # There are some points within the max distance so get them.
                if indexes:
                    near_points = self._get_result_points(indexes)

                else:
                    near_points = ()

            # Only 1 point was requested/found.
            else:
                # If the point is within the distances, glob and return it.
                if distances < maxdist:
                    near_points = self._get_result_points([indexes])

                else:
                    near_points = ()

        #  We don't care about the points being within a certain distance.
        else:
            # If the point list is an array then more than one point was found.
            if isinstance(indexes, numpy.ndarray):
                near_points = self._get_result_points(indexes.tolist())

            else:
                # We found a single point, so pass it along in a tuple..
                near_points = self._get_result_points([indexes])

        # Return the tuple of points.
        return near_points
