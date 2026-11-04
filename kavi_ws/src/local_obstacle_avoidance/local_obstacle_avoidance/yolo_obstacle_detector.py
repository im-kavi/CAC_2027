#!/usr/bin/env python3
"""
Reactive Obstacle Avoidance Supervisor Node.
Subscribes to /cmd_vel_nav (from Nav2 or joystick) and /local_obstacles/pointcloud or /warning,
and outputs safe /cmd_vel to the robot base controller.
If an obstacle is critically close directly ahead, it stops the rover or slows down.
"""

import math
import struct
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool


class ReactiveAvoidanceNode(Node):
    def __init__(self):
        super().__init__('reactive_avoidance_node')

        self.declare_parameter('input_cmd_vel', '/cmd_vel_nav')
        self.declare_parameter('output_cmd_vel', '/cmd_vel')
        self.declare_parameter('stop_distance', 0.50)  # meters
        self.declare_parameter('slowdown_distance', 0.90)  # meters
        self.declare_parameter('corridor_width', 0.60)  # rover width buffer

        self.in_topic = self.get_parameter('input_cmd_vel').value
        self.out_topic = self.get_parameter('output_cmd_vel').value
        self.stop_dist = self.get_parameter('stop_distance').value
        self.slow_dist = self.get_parameter('slowdown_distance').value
        self.corridor_w = self.get_parameter('corridor_width').value

        self.min_obstacle_dist = float('inf')

        # Pub / Sub
        self.cmd_pub = self.create_publisher(Twist, self.out_topic, 10)
        self.create_subscription(Twist, self.in_topic, self._cmd_cb, 10)
        self.create_subscription(PointCloud2, '/local_obstacles/pointcloud', self._cloud_cb, 10)

        self.get_logger().info(
            f"Reactive Avoidance Supervisor active: {self.in_topic} -> {self.out_topic} "
            f"(Stop: {self.stop_dist}m, Slow: {self.slow_dist}m)")

    def _cloud_cb(self, msg: PointCloud2):
        min_d = float('inf')
        point_step = msg.point_step
        num_points = msg.width * msg.height

        # Parse X, Y, Z (assuming float32 at offsets 0, 4, 8)
        data = msg.data
        for i in range(num_points):
            offset = i * point_step
            if offset + 12 <= len(data):
                x, y, z = struct.unpack_from('fff', data, offset)
                # In camera optical frame: Z is forward, X is right, Y is down
                # If frame is camera optical: forward = z, lateral = x
                # Check if obstacle is inside lateral corridor
                if abs(x) < (self.corridor_w / 2.0) and z > 0.05:
                    if z < min_d:
                        min_d = z

        self.min_obstacle_dist = min_d

    def _cmd_cb(self, in_cmd: Twist):
        out_cmd = Twist()
        out_cmd.angular = in_cmd.angular

        # Only restrict forward motion
        if in_cmd.linear.x > 0.0:
            if self.min_obstacle_dist < self.stop_dist:
                # Critical stop
                out_cmd.linear.x = 0.0
                self.get_logger().warn(
                    f"Obstacle detected at {self.min_obstacle_dist:.2f}m! Stopping rover.",
                    throttle_duration_sec=1.0)
            elif self.min_obstacle_dist < self.slow_dist:
                # Proportional slowdown
                factor = (self.min_obstacle_dist - self.stop_dist) / (self.slow_dist - self.stop_dist)
                out_cmd.linear.x = in_cmd.linear.x * max(0.2, factor)
            else:
                out_cmd.linear.x = in_cmd.linear.x
        else:
            # Reverse allowed
            out_cmd.linear.x = in_cmd.linear.x

        self.cmd_pub.publish(out_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ReactiveAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
