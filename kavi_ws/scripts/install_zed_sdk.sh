#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "=========================================================="
echo "Building Kavi ROS 2 Workspace (ROS 2 Jazzy)"
echo "Packages: arena_map, local_obstacle_avoidance, zed_ros2"
echo "=========================================================="

source /opt/ros/jazzy/setup.bash

# Check ZED SDK availability
if [ ! -d "/usr/local/zed" ]; then
    echo "NOTICE: /usr/local/zed was not found."
    echo "Building arena_map, local_obstacle_avoidance, zed_msgs, zed_description, and nmea_msgs."
    colcon build --symlink-install \
        --packages-select arena_map local_obstacle_avoidance arena_nav2 zed_msgs zed_description nmea_msgs
else
    echo "Found ZED SDK at /usr/local/zed."
    echo "Building all packages with colcon..."
    colcon build --symlink-install \
        --cmake-args=-DCMAKE_BUILD_TYPE=Release \
        --parallel-workers $(nproc)
fi

echo "=========================================================="
echo "Build complete!"
echo "To source this workspace in your terminal:"
echo "    source ${SCRIPT_DIR}/install/setup.bash"
echo ""
echo "To launch static arena map with masked zones:"
echo "    ros2 launch arena_map arena_map.launch.py"
echo ""
echo "To launch local obstacle avoidance with YOLO (best.pt):"
echo "    ros2 launch local_obstacle_avoidance obstacle_detector.launch.py"
echo ""
echo "To launch full static map navigation + local avoidance:"
echo "    ros2 launch local_obstacle_avoidance arena_nav_avoidance.launch.py"
echo "=========================================================="
