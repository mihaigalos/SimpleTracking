"""
Simple object tracking implemented in Python 2 using ROS and PyKalman.
"""
#!/usr/bin/env python

import collections  # for deque
from pykalman import KalmanFilter
import rviz_tools_py as rviz_tools
import rospy

from cinematic_models import ConstantAccelerationPoseCalculator


class KalmanWrapper(object):
    """
    Wrapper for configuring and passing values to and from the Kalman KalmanFilter.
    """

    def __init__(self):
        """
        Transition matrix has form [x, x_dot, y, y_dot].
        Observation matrix has same form.
        """
        self.transition_matrix = [[1, 1, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 1],
                                  [0, 0, 0, 1]]

        self.observation_matrix = [[1, 0, 0, 0],
                                   [0, 0, 1, 0]]

    def make_prediction(self, measurements):
        """
        Compute prediction of object position for the next step.
        """
        initial_state_mean = [measurements[0][0], 0,
                              measurements[0][1], 0]

        kf1 = KalmanFilter(transition_matrices=self.transition_matrix,
                           observation_matrices=self.observation_matrix,
                           initial_state_mean=initial_state_mean)
        kf1 = kf1.em(list(measurements), n_iter=2)
        return kf1.smooth(measurements)

    def get_prediction(self, measurements):
        """
        Compute object position prediction based on current state and Kalman filter's
        parameters.
        """
        prediction = self.make_prediction(measurements)
        return prediction[0]


class Tracking(object):
    """
    Actual tracking implementation.
    """

    def __init__(self, cinematic_model):

        self.markers = None
        self.update_frecuency = 100.0
        self.cinematic_model = cinematic_model

        rospy.init_node('tracking', anonymous=False,
                        log_level=rospy.INFO, disable_signals=False)
        rospy.on_shutdown(self.cleanup_node)
        self.markers = rviz_tools.RvizMarkers('/map', 'visualization_marker')

        self.kalman_wrapper = KalmanWrapper()
        self.deque = collections.deque(maxlen=2)
        self.i = 0

    def cleanup_node(self):
        """
        Teardown method.
        """
        print "Shutting down node"
        self.markers.deleteAllMarkers()

    def run(self):
        """
        Periodic update object position and tracking.
        """
        while not rospy.is_shutdown():
            new_pose = self.cinematic_model.get_new_pose()
            cube_width = 0.6
            # pose, color, cube_width, lifetime
            self.markers.publishCube(new_pose, 'green', cube_width,
                                     1 / self.update_frecuency)

            self.deque.append([new_pose.position.x, new_pose.position.y])
            if self.i > 2:
                tracked_pose = new_pose
                prediction = self.kalman_wrapper.get_prediction(self.deque)

                tracked_pose.position.x = prediction[0][0]
                tracked_pose.position.y = prediction[0][2]

                self.markers.publishCube(tracked_pose, 'translucent',
                                         cube_width + 0.1, 1 / self.update_frecuency)
            self.i = self.i + 1

            rospy.Rate(self.update_frecuency).sleep()


Tracking(ConstantAccelerationPoseCalculator()).run()
