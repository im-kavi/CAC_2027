<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
            schemalocation="http://www.w3.org/2001/XMLSchema-instance"?>
<package format="3">
  <name>arena_map</name>
  <version>1.0.0</version>
  <description>
    Static NAV2 occupancy map for the UK Lunabotics arena (9 m x 5 m) plus
    a colored RViz2 zone-overlay publisher. Four zones are laid out with
    exact dimensions (Starting 2 m x 2.5 m, Construction 2 m x 1.5 m,
    Obstacle 5.5 m x 5 m, Excavation 1.5 m x 5 m); rocks and craters are
    NOT included in the occupancy grid.
  </description>

  <maintainer email="user@todo.todo">user</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>visualization_msgs</exec_depend>
  <exec_depend>nav_msgs</exec_depend>
  <exec_depend>launch</exec_depend>
  <exec_depend>launch_ros</exec_depend>
  <exec_depend>nav2_map_server</exec_depend>
  <exec_depend>nav2_lifecycle_manager</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
