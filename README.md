# BARAM Manipulator

ROS 2 packages for the `baram` manipulator.

- arm joints: `joint1` to `joint6`
- arm Dynamixel IDs: `0` to `5`
- arm launch: `open_manipulator_bringup`
- robot description: `open_manipulator_description`

## Start BARAM Controller

```bash
cd
git clone https://github.com/YoungWook0533/BARAM_manipulator.git
```

Start the Docker container from the repository:

```bash
cd BARAM_manipulator/docker
./container.sh start
```

On same directory, enter container:

```bash
./container.sh enter
```

Inside Docker, install the gripper dependency:

```bash
sudo apt update
sudo apt install python3-serial
```

Replace the default `dynamixel_hardware_interface` with the BARAM fork:

```bash
cd ~/ros2_ws/src
rm -rf dynamixel_hardware_interface
git clone https://github.com/YoungWook0533/dynamixel_hardware_interface.git
```

Build in `ros2_ws` with `cb`, then source the workspace:

```bash
cd ~/ros2_ws
cb
source install/setup.bash
```

## Launch

Launch the BARAM arm controller:

```bash
ros2 launch open_manipulator_bringup baram.launch.py
```

Launch with gripper:

```bash
ros2 launch open_manipulator_bringup baram.launch.py gripper:=true
```

Launch with RViz:

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

Additional dependency:

```bash
sudo apt update
sudo apt install python3-serial
```

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
