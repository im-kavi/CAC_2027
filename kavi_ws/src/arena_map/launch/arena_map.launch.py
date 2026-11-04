# Starter NAV2 parameters for the UK Lunabotics arena.
# Tune robot_radius/footprint to match your rover before running a full stack.
# Rover spec from diagram: 1.5 m x 0.75 m x 0.75 m, 80 kg max.
amcl:
  ros__parameters:
    use_sim_time: false
    base_frame_id: "base_link"
    odom_frame_id: "odom"
    global_frame_id: "map"
    robot_model_type: "nav2_amcl::DifferentialMotionModel"

bt_navigator:
  ros__parameters:
    use_sim_time: false
    global_frame: map
    robot_base_frame: base_link

controller_server:
  ros__parameters:
    use_sim_time: false
    controller_frequency: 10.0
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"

planner_server:
  ros__parameters:
    use_sim_time: false
    expected_planner_frequency: 5.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner::NavfnPlanner"

behavior_server:
  ros__parameters:
    use_sim_time: false

map_server:
  ros__parameters:
    use_sim_time: false
    yaml_filename: ""       # override from launch file

local_costmap:
  local_costmap:
    ros__parameters:
      use_sim_time: false
      global_frame: odom
      robot_base_frame: base_link
      update_frequency: 5.0
      publish_frequency: 2.0
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.02
      robot_radius: 0.50
      plugins: ["obstacle_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: true

global_costmap:
  global_costmap:
    ros__parameters:
      use_sim_time: false
      global_frame: map
      robot_base_frame: base_link
      update_frequency: 1.0
      publish_frequency: 1.0
      resolution: 0.02
      robot_radius: 0.50
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: true
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55

lifecycle_manager_navigation:
  ros__parameters:
    use_sim_time: false
    autostart: true
    node_names:
      - controller_server
      - planner_server
      - behavior_server
      - bt_navigator
