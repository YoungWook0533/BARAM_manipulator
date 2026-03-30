# BARAM Manipulator

ROS 2 packages for the `baram` manipulator.

- arm joints: `joint1` to `joint6`
- arm Dynamixel IDs: `0` to `5`
- arm launch: `open_manipulator_bringup`
- robot description: `open_manipulator_description`

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select dynamixel_hardware_interface open_manipulator_description open_manipulator_bringup
source install/setup.bash
```

## Launch

Real robot:

```bash
ros2 launch open_manipulator_bringup baram.launch.py
```

With RViz:

```bash
ros2 launch open_manipulator_bringup baram.launch.py start_rviz:=true
```

Without initial motion:

```bash
ros2 launch open_manipulator_bringup baram.launch.py init_position:=false
```

With mock hardware:

```bash
ros2 launch open_manipulator_bringup baram.launch.py use_mock_hardware:=true
```

Gazebo:

```bash
ros2 launch open_manipulator_bringup baram_gazebo.launch.py
```

## Home Pose

Loaded from `open_manipulator_bringup/config/baram/initial_positions.yaml`.

```text
[0.0, 0.7770062579651399, 2.1978436317113994, -0.002471903355417154, 1.4730475459913506, -0.008791288084119586]
```

## Arm Commands

Check controllers:

```bash
ros2 control list_controllers
```

Check joint states:

```bash
ros2 topic echo /joint_states
```

Zero pose:

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

Home pose:

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

Custom example:

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

## Gripper

Default gripper settings:

- executable: `baram_gripper_controller`
- port: `/dev/ttyUSB1`
- baudrate: `1000000`
- topic: `/gripper`

Launch arm with gripper:

```bash
ros2 launch open_manipulator_bringup baram.launch.py gripper:=true
```

Run only gripper:

```bash
ros2 run open_manipulator_bringup baram_gripper_controller
```

Run gripper with custom port:

```bash
ros2 run open_manipulator_bringup baram_gripper_controller --ros-args -p device_name:=/dev/ttyUSB1 -p baudrate:=1000000
```

Open:

```bash
ros2 topic pub --once /gripper std_msgs/msg/UInt8 "{data: 0}"
```

Close:

```bash
ros2 topic pub --once /gripper std_msgs/msg/UInt8 "{data: 1}"
```

Emergency stop:

```bash
ros2 topic pub --once /estop std_msgs/msg/Bool "{data: true}"
```

Command values:

- `0` = open
- `1` = close
