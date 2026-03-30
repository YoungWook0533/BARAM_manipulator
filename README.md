# BARAM Manipulator

This repository contains ROS 2 packages for the `baram` manipulator.

The `baram` robot is a 6-DOF manipulator using:
- `joint1` to `joint6`
- Dynamixel IDs `0` to `5`
- `open_manipulator_bringup` for launch
- `open_manipulator_description` for URDF/xacro and ros2_control

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select dynamixel_hardware_interface open_manipulator_description open_manipulator_bringup
source install/setup.bash
```

## Launch

Launch the real robot:

```bash
ros2 launch open_manipulator_bringup baram.launch.py
```

Launch with RViz:

```bash
ros2 launch open_manipulator_bringup baram.launch.py start_rviz:=true
```

Launch without the initial home motion:

```bash
ros2 launch open_manipulator_bringup baram.launch.py init_position:=false
```

Launch with mock hardware:

```bash
ros2 launch open_manipulator_bringup baram.launch.py use_mock_hardware:=true
```

Launch Gazebo:

```bash
ros2 launch open_manipulator_bringup baram_gazebo.launch.py
```

## Home Position

The default home pose is loaded from `open_manipulator_bringup/config/baram/initial_positions.yaml`.

```text
[0.0, 0.7770062579651399, 2.1978436317113994, -0.002471903355417154, 1.4730475459913506, -0.008791288084119586]
```

## Example Commands

Check available controllers:

```bash
ros2 control list_controllers
```

Check joint states:

```bash
ros2 topic echo /joint_states
```

Send all joints to zero:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "
joint_names:
- joint1
- joint2
- joint3
- joint4
- joint5
- joint6
points:
- positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  time_from_start:
    sec: 7
    nanosec: 0
"
```

Send the robot to the configured home pose:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "
joint_names:
- joint1
- joint2
- joint3
- joint4
- joint5
- joint6
points:
- positions: [0.0, 0.7770062579651399, 2.1978436317113994, -0.002471903355417154, 1.4730475459913506, -0.008791288084119586]
  velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  time_from_start:
    sec: 7
    nanosec: 0
"
```

Send a custom example motion:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "
joint_names:
- joint1
- joint2
- joint3
- joint4
- joint5
- joint6
points:
- positions: [0.0, 0.5, 1.8, 0.0, 1.2, 0.0]
  velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  time_from_start:
    sec: 7
    nanosec: 0
"
```
