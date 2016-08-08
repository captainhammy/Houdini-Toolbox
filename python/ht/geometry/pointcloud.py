"""Module to represent geometry as a point cloud in Houdini."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import numpy
from scipy.spatial import KDTree

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================


class PointCloud(object):
    """A wrapper around scipy.spatial.KDTree to represent point positions.

    """

    def __init__(self, geometry, pattern=None, leaf_size=10):
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

        # Build the tree from the data.
        self._tree = KDTree(data, leaf_size)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<PointCloud from {}>".format(self._geometry.sopNode().path())

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _getResultPoints(self, indexes):
        """This method converts a list of integers into corresponding hou.Point
        objects belonging to the geometry depending on whether a point map is
        being used.

        """
        # If we have a point map set up we need to index into that and then
        # convert to string.
        if self._point_map:
            pattern = " ".join(
                [str(self._point_map[index]) for index in indexes]
            )

        # Just convert the indexes to strings.
        else:
            pattern = " ".join([str(index) for index in indexes])

        # Try to return our matched points.
        try:
            return self._geometry.globPoints(pattern)

        # If we didn't find any points then the pattern will be invalid and
        # throw an exception.  Catch it and return an empty tuple.
        except hou.OperationFailed:
            return ()

    # =========================================================================
    # METHODS
    # =========================================================================

    def findAllClosePoints(self, position, maxdist):
        """Find all points within the maxdist from the position."""
        # Convert the position to a compatible ndarray.
        positions = numpy.array([position])

        # Perform a query based on the position and maxdist.
        result = self._tree.query_ball_point(positions, maxdist)

        # Return any points that are found.
        return self._getResultPoints(result[0])

    def findNearestPoints(self, position, num_points=1, maxdist=None):
        """Find the closest N points to the position"""
        # Make sure we aren't querying for more points than we have.
        if num_points > self._num_elements:
            num_points = self._num_elements

        # Return no points if we ask for an invalid number of points.
        if num_points < 1:
            return ()

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
                indexes = [index for dist, index in zip(distances, indexes)
                           if dist < maxdist]

                # There are some points within the max distance so get them.
                if len(indexes) > 0:
                    near_points = self._getResultPoints(indexes)

                else:
                    near_points = ()

            # Only 1 point was requested/found.
            else:
                # If the point is within the distances, glob and return it.
                if distances < maxdist:
                    near_points = self._getResultPoints((indexes, ))

                else:
                    near_points = ()

        #  We don't care about the points being within a certain distance.
        else:
            # If the point list is an array then more than one point was found.
            if isinstance(indexes, numpy.ndarray):
                near_points = self._getResultPoints(indexes.tolist())

            else:
                # We found a single point, so pass it along in a tuple..
                near_points = self._getResultPoints((indexes, ))

        # Return the tuple of points.
        return near_points

