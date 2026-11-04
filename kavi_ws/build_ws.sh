# Kavi ROS 2 Workspace (`kavi_ws`)

A unified ROS 2 Jazzy workspace for the **Lunabotics / CAC_27 Arena Robot**, integrating:
1. **`arena_map`**: Static 9 m x 5 m arena map with colored zone overlays (Starting Zone, Obstacle Zone, Construction Zone, Excavation Zone, Berm Zone).
2. **`local_obstacle_avoidance`**: Real-time Crater & Rock obstacle detection and avoidance using YOLOv8 segmentation (`best.pt`) projected to 3D pointclouds and integrated into Nav2 costmaps.
3. **`zed_ros2`**: Stereolabs ZED stereo camera ROS 2 wrapper, description URDFs, messages, and NMEA GPS packages.

---

## Workspace Structure

```
kavi_ws/
├── build_ws.sh                        # Build script for all packages
├── scripts/
│   ├── install_zed_sdk.sh             # ZED SDK setup script
│   ├── setup_prerequisites.sh         # Prerequisites installer
│   ├── zed.repos                      # Upstream repo manifests
│   └── zed_sdk/                       # ZED SDK installer binary
│       └── ZED_SDK_...zstd.run
├── src/
│   ├── arena_map/                     # Static map & zone overlay package
│   │   ├── arena_map/
│   │   │   └── zone_markers.py        # Publishes /arena/zones MarkerArray
│   │   ├── maps/
│   │   │   ├── arena_map.pgm          # 450x250 px, 0.02 m/px binary map
│   │   │   ├── arena_map.yaml         # nav2_map_server configuration
│   │   │   └── gen_map.py             # Script to regenerate map
│   │   ├── launch/
│   │   │   └── arena_map.launch.py    # Map server, lifecycle manager & RViz
│   │   └── rviz/
│   │       └── arena_map.rviz
│   │
│   ├── local_obstacle_avoidance/       # Local obstacle avoidance with best.pt
│   │   ├── models/
│   │   │   └── best.pt                # Trained YOLOv8s-seg model (Crater + Rock)
│   │   ├── local_obstacle_avoidance/
│   │   │   ├── yolo_obstacle_detector.py   # YOLO inference & 3D pointcloud projection
│   │   │   └── reactive_avoidance_node.py  # Emergency obstacle slowdown/stop
│   │   ├── config/
│   │   │   ├── detector_params.yaml        # Detection thresholds & topic mappings
│   │   │   └── nav2_arena_avoidance.yaml   # Nav2 params: static global map + local obstacle layer
│   │   ├── launch/
│   │   │   ├── obstacle_detector.launch.py # Detector & 3D cloud publisher
│   │   │   └── arena_nav_avoidance.launch.py # Full stack with RViz
│   │   └── rviz/
│   │       └── arena_nav_avoidance.rviz
│   │
│   └── zed_ros2/                      # ZED Stereo Camera Packages
│       ├── zed-ros2-wrapper/          # zed_wrapper, zed_components, zed_ros2, zed_debug
│       ├── zed-ros2-interfaces/       # zed_msgs
│       ├── zed-ros2-description/      # zed_description
│       └── nmea_msgs/                 # GPS NMEA message definitions
```

---

## Arena Zones Overview (9 m x 5 m)

| Zone | Dimensions | Coordinates | Visual Overlay |
| :--- | :--- | :--- | :--- |
| **Starting Zone** | 2.0 m x 2.5 m | (0.0, 2.5) | Light Green |
| **Obstacle Corridor** | 2.0 m x 1.0 m | (0.0, 1.5) | Transparent |
| **Construction Zone** | 2.0 m x 1.5 m | (0.0, 0.0) | Light Blue |
| **Obstacle Zone** | 5.5 m x 5.0 m | (2.0, 0.0) | White outline (Dynamic Craters & Rocks) |
| **Excavation Zone** | 1.5 m x 5.0 m | (7.5, 0.0) | Light Pink |
| **Berm Zone** | 1.25 m x 0.9 m | (0.375, 0.3) | Red |

---

## How Obstacle Avoidance Works

1. **Global Planning (Static Map)**:
   - Nav2 loads `arena_map.yaml` into the global costmap `static_layer`.
   - The global path is planned between zones while respecting outer perimeter walls.
2. **Local Avoidance (best.pt + Depth)**:
   - `yolo_obstacle_detector` processes the RGB camera stream and identifies `Crater` and `Rock` segmentation masks.
   - Using the synchronized ZED depth stream, the 2D mask pixels are back-projected into a 3D obstacle point cloud published on `/local_obstacles/pointcloud`.
   - Nav2's `local_costmap` `obstacle_layer` subscribes to `/local_obstacles/pointcloud`, dynamically marking detected craters and rocks as lethal obstacles.
   - The local planner (DWB) plans avoidance trajectories around detected obstacles on-the-fly.
3. **Visual Markers**:
   - 3D markers and distance labels are published to `/local_obstacles/markers` for monitoring in RViz2.

---

## Build Instructions

```bash
cd ~/CAC_27/kavi_ws
./build_ws.sh
# Or manually:
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

Source the workspace:
```bash
source ~/CAC_27/kavi_ws/install/setup.bash
```

---

## Running

### 1. View Static Map with Zone Overlays
```bash
ros2 launch arena_map arena_map.launch.py
```

### 2. Run Local Obstacle Detection with `best.pt`
```bash
ros2 launch local_obstacle_avoidance obstacle_detector.launch.py
```

### 3. Run Static Map Navigation with Local Obstacle Avoidance
```bash
ros2 launch local_obstacle_avoidance arena_nav_avoidance.launch.py
```

### 4. Launch ZED Camera (ZED 2 / ZED 2i / ZED X)
```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2i
```

### 5. Launch NAV2 (Hybrid A* global planner + MPPI local controller)
```bash
ros2 launch arena_nav2 nav2_hybrid_mppi.launch.py
```
Loads the static arena map, manual localization, the NAV2 stack (Hybrid A*
global planner, MPPI local controller, behavior tree navigator) and RViz2 with a
preconfigured view. Generates `cmd_vel` (via `cmd_vel_nav`/velocity smoother)
for the rover.

Prefer `full_stack.launch.py` (same stack, plus YOLO detection, the URDF robot
model and the ZED->base transform):

```bash
ros2 launch arena_nav2 full_stack.launch.py
```

#### Workflow

1. Start the ZED wrapper with `publish_map_tf:=false` (it must not publish
   `map -> odom`).
2. In RViz click **2D Pose Estimate** and drag at the robot's position: this
   publishes `/initialpose`, and `manual_initial_pose` recomputes `map -> odom`
   so the robot model moves to the clicked pose.
3. Click **Nav2 Goal** and drag at the destination (drag sets the heading). The
   goal goes to `/navigate_to_pose`; Hybrid A* publishes the green path on
   `/plan` from the new pose to the clicked point.

#### Costmap notes

* The occupancy grid contains only the 9 x 5 m rectangle; the colored zones are
  RViz markers (`/arena/zones`) and never affect planning.
* Costmaps take dynamic obstacles from the YOLO crater/rock cloud
  (`/local_obstacles/pointcloud`). The raw ZED cloud is shown in RViz as
  `ZED Point Cloud (debug)` (disabled by default) but is deliberately not fed to
  the costmaps, because it sees the whole room and would block the arena.
* `robot_radius: 0.28` and `inflation_radius: 0.35` are used in both costmaps.

#### Launch options

```bash
ros2 launch arena_nav2 full_stack.launch.py use_rviz:=false        # headless
ros2 launch arena_nav2 full_stack.launch.py use_yolo:=false        # no detector
ros2 launch arena_nav2 full_stack.launch.py use_amcl:=true         # AMCL + depth->scan
ros2 launch arena_nav2 full_stack.launch.py publish_dummy_tf:=true # no ZED
ros2 launch arena_nav2 full_stack.launch.py initial_x:=4.5 initial_y:=2.5
```

#### Quick checks

```bash
ros2 topic hz /local_obstacles/debug_image     # YOLO view
ros2 topic hz /plan                            # Hybrid A* path after a goal
ros2 run tf2_ros tf2_echo map base_link        # localized pose
```

If no green path appears, make sure only one stack is running (duplicate
`planner_server` / `manual_initial_pose` processes fight over `/tf`), and that the
goal is inside the arena and not inside wall or obstacle inflation.
