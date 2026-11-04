#!/usr/bin/env python3
"""Dummy ZED 2i publisher for bench-testing the trial_bot Nav2 stack.

Replaces the real zed_wrapper by publishing the topics/TF that trial_bot
expects from the camera, without touching the launch file:

  * /zed/zed_node/odom            (nav_msgs/Odometry, odom -> pose at origin)
  * static TF  odom -> zed_camera_link   (same as publish_dummy_tf:=true)
  * /zed/zed_node/rgb/color/rect/image  (sensor_msgs/Image test pattern)

NOTES
-----
  * Run this INSTEAD of using publish_dummy_tf:=true on the launch file,
    so the two static TFs don't fight each other:
        Terminal 1:  ros2 run trial_bot dummy ... or python3 scripts/dummy_zed2i.py
        Terminal 2:  ros2 launch trial_bot trial_bot.launch.py
  * Set --motion to make the fake odometry drift forward slowly so you can
    see the costmap/robot move on the map.
"""
import argparse
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovariance, TwistWithCovariance, Pose, Twist, Point, Quaternion, Vector3
from sensor_msgs.msg import Image
from tf2_ros import TransformBroadcaster, TransformStamped
from std_msgs.msg import Header

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False


class DummyZed2i(Node):
    def __init__(self, rate_hz: float, motion: float, image: bool):
        super().__init__('dummy_zed2i')
        self.motion = motion
        self.start = self.get_clock().now().nanoseconds / 1e9

        odom_qos = QoSProfile(depth=10,
                              reliability=ReliabilityPolicy.RELIABLE,
                              history=HistoryPolicy.KEEP_LAST)
        self.odom_pub = self.create_publisher(Odometry, '/zed/zed_node/odom', odom_qos)

        self.tf_broadcaster = TransformBroadcaster(self)

        self.image_pub = None
        if image:
            image_qos = QoSProfile(depth=5,
                                   reliability=ReliabilityPolicy.RELIABLE,
                                   history=HistoryPolicy.KEEP_LAST)
            self.image_pub = self.create_publisher(Image,
                                                  '/zed/zed_node/rgb/color/rect/image',
                                                  image_qos)

        self.create_timer(1.0 / rate_hz, self._publish)

        self.get_logger().info(
            'Dummy ZED 2i publishing on /zed/zed_node/odom'
            + (' + RGB image' if image else '')
            + f' with odom -> zed_camera_link TF (motion={motion} m/s)')

    def _odom(self, t: float) -> Odometry:
        msg = Odometry()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'zed_camera_link'

        x = self.motion * t
        msg.pose = PoseWithCovariance(pose=Pose(
            position=Point(x=x, y=0.0, z=0.0),
            orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)))
        msg.twist = TwistWithCovariance(twist=Twist(
            linear=Vector3(x=self.motion, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.0)))
        return msg

    def _tfer(self, x: float, y: float, z: float, yaw: float = 0.0) -> TransformStamped:
        tf = TransformStamped()
        tf.header.stamp = self.get_clock().now().to_msg()
        tf.header.frame_id = 'odom'
        tf.child_frame_id = 'zed_camera_link'
        tf.transform.translation.x = float(x)
        tf.transform.translation.y = float(y)
        tf.transform.translation.z = float(z)
        tf.transform.rotation = Quaternion(
            x=0.0, y=0.0, z=math.sin(yaw * 0.5), w=math.cos(yaw * 0.5))
        return tf

    def _test_image(self) -> Image or None:
        if not HAVE_NUMPY:
            return None
        h, w = 360, 640
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = (40, 90, 40)  # dark greenish backdrop like the arena floor
        # moving marker so you can see the "camera" is alive
        t = self.get_clock().now().nanoseconds / 1e9
        cx = int((t * 80) % w)
        frame[:, max(0, cx - 20):cx, :] = (0, 200, 255)
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'zed_camera_link'
        msg.height = h
        msg.width = w
        msg.encoding = 'bgr8'
        msg.is_bigendian = 0
        msg.step = w * 3
        msg.data = frame.tobytes()
        return msg

    def _publish(self):
        t = self.get_clock().now().nanoseconds / 1e9 - self.start
        x = self.motion * t

        self.odom_pub.publish(self._odom(t))
        self.tf_broadcaster.sendTransform(self._tfer(x, 0.0, 0.0))
        if self.image_pub is not None:
            img = self._test_image()
            if img is not None:
                self.image_pub.publish(img)


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rate', type=float, default=10.0,
                        help='Publishing rate in Hz (default 10)')
    parser.add_argument('--motion', type=float, default=0.0,
                        help='Fake forward speed in m/s (default 0 = stationary)')
    parser.add_argument('--no-image', action='store_true',
                        help='Skip publishing the test-pattern image')
    known, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args)
    node = DummyZed2i(known.rate, known.motion, not known.no_image)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
