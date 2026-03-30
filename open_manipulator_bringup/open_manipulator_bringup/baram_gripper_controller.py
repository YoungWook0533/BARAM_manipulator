#!/usr/bin/env python3

from dynamixel_sdk import COMM_SUCCESS
from dynamixel_sdk import PacketHandler
from dynamixel_sdk import PortHandler
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_msgs.msg import UInt8

# Protocol 1.0 control table addresses used by the original gripper setup.
RX_ADDR_TORQUE_ENABLE = 24
RX_ADDR_GOAL_POSITION = 30
RX_ADDR_MOVING_SPEED = 32
RX_ADDR_CW_COMPLIANCE_SLOPE = 28
RX_ADDR_CCW_COMPLIANCE_SLOPE = 29

MX_ADDR_TORQUE_ENABLE = 24
MX_ADDR_GOAL_POSITION = 30
MX_ADDR_MOVING_SPEED = 32
MX_ADDR_P_GAIN = 28

PROTOCOL_VERSION = 1.0
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DEFAULT_MOVING_SPEED = 50

RX_RAD2POS = 197.5716
MX_RAD2POS = 651.0884


class BaramGripperController(Node):
    def __init__(self):
        super().__init__('baram_gripper_controller')

        self.declare_parameter('device_name', '/dev/ttyUSB1')
        self.declare_parameter('baudrate', 1000000)
        self.declare_parameter('command_topic', '/gripper')
        self.declare_parameter('estop_topic', '/estop')
        self.declare_parameter('timer_period', 0.1)
        self.declare_parameter('default_moving_speed', DEFAULT_MOVING_SPEED)
        self.declare_parameter('motor_ids', [9, 10, 11])
        self.declare_parameter('model_types', [28, 29, 29])
        self.declare_parameter('open_rads', [2.70491127, 3.57565604, 2.1675244])
        self.declare_parameter('close_rads', [2.0944, 4.3456953, 2.76268167])
        self.declare_parameter('mx_p_gain', 12)
        self.declare_parameter('rx_compliance_slope', 254)

        self.device_name = self.get_parameter('device_name').value
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.command_topic = self.get_parameter('command_topic').value
        self.estop_topic = self.get_parameter('estop_topic').value
        self.timer_period = float(self.get_parameter('timer_period').value)
        self.default_moving_speed = int(
            self.get_parameter('default_moving_speed').value
        )
        self.motor_ids = list(self.get_parameter('motor_ids').value)
        self.model_types = list(self.get_parameter('model_types').value)
        self.open_rads = list(self.get_parameter('open_rads').value)
        self.close_rads = list(self.get_parameter('close_rads').value)
        self.mx_p_gain = int(self.get_parameter('mx_p_gain').value)
        self.rx_compliance_slope = int(
            self.get_parameter('rx_compliance_slope').value
        )

        num_motors = len(self.motor_ids)
        if not (
            len(self.model_types) == num_motors
            and len(self.open_rads) == num_motors
            and len(self.close_rads) == num_motors
        ):
            raise ValueError('motor_ids, model_types, open_rads, close_rads lengths must match')

        self.port_handler = PortHandler(self.device_name)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

        self.grip_cmd = 0
        self.command_received = False
        self.estop = False

        self._open_port()
        self._initialize_motors()

        self.command_sub = self.create_subscription(
            UInt8, self.command_topic, self.gripper_callback, 10
        )
        self.estop_sub = self.create_subscription(
            Bool, self.estop_topic, self.estop_callback, 10
        )
        self.timer = self.create_timer(self.timer_period, self.write_gripper_callback)

        self.get_logger().info(
            f'Gripper controller ready on {self.device_name} at {self.baudrate} bps'
        )

    def _open_port(self):
        if not self.port_handler.openPort():
            raise RuntimeError(f'Cannot open {self.device_name}')
        if not self.port_handler.setBaudRate(self.baudrate):
            raise RuntimeError(f'Cannot set baudrate to {self.baudrate}')

    def _write_1byte(self, motor_id, address, value, context):
        comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
            self.port_handler, motor_id, address, value
        )
        if comm_result != COMM_SUCCESS:
            raise RuntimeError(
                f'ID {motor_id} {context} failed: '
                f'{self.packet_handler.getTxRxResult(comm_result)}'
            )
        if dxl_error != 0:
            raise RuntimeError(
                f'ID {motor_id} {context} packet error: '
                f'{self.packet_handler.getRxPacketError(dxl_error)}'
            )

    def _write_2byte(self, motor_id, address, value, context):
        comm_result, dxl_error = self.packet_handler.write2ByteTxRx(
            self.port_handler, motor_id, address, value
        )
        if comm_result != COMM_SUCCESS:
            raise RuntimeError(
                f'ID {motor_id} {context} failed: '
                f'{self.packet_handler.getTxRxResult(comm_result)}'
            )
        if dxl_error != 0:
            raise RuntimeError(
                f'ID {motor_id} {context} packet error: '
                f'{self.packet_handler.getRxPacketError(dxl_error)}'
            )

    def _goal_radians_to_raw(self, radians, model_type):
        scale = RX_RAD2POS if model_type == 28 else MX_RAD2POS
        return int(radians * scale)

    def _initialize_motors(self):
        for motor_id, model_type in zip(self.motor_ids, self.model_types):
            torque_addr = (
                RX_ADDR_TORQUE_ENABLE if model_type == 28 else MX_ADDR_TORQUE_ENABLE
            )
            speed_addr = RX_ADDR_MOVING_SPEED if model_type == 28 else MX_ADDR_MOVING_SPEED

            self._write_1byte(motor_id, torque_addr, TORQUE_ENABLE, 'torque enable')
            self._write_2byte(
                motor_id, speed_addr, self.default_moving_speed, 'speed write'
            )

            if model_type == 29:
                self._write_1byte(motor_id, MX_ADDR_P_GAIN, self.mx_p_gain, 'P gain write')
            else:
                self._write_1byte(
                    motor_id,
                    RX_ADDR_CW_COMPLIANCE_SLOPE,
                    self.rx_compliance_slope,
                    'CW compliance write',
                )
                self._write_1byte(
                    motor_id,
                    RX_ADDR_CCW_COMPLIANCE_SLOPE,
                    self.rx_compliance_slope,
                    'CCW compliance write',
                )

            self.get_logger().info(f'Initialized gripper motor ID {motor_id}')

    def gripper_callback(self, msg: UInt8):
        if msg.data <= 1:
            self.grip_cmd = int(msg.data)
            self.command_received = True
            state = 'CLOSE' if self.grip_cmd else 'OPEN'
            self.get_logger().info(f'Gripper command: {state}')
        else:
            self.get_logger().warn(f'Invalid gripper command {msg.data} (use 0=open, 1=close)')

    def estop_callback(self, msg: Bool):
        if msg.data and not self.estop:
            self.estop = True
            self.get_logger().error('Emergency stop activated for gripper')

    def write_gripper_callback(self):
        if self.estop or not self.command_received:
            return

        self.command_received = False
        target_rads = self.close_rads if self.grip_cmd else self.open_rads

        for motor_id, model_type, target_rad in zip(
            self.motor_ids, self.model_types, target_rads
        ):
            goal_position = self._goal_radians_to_raw(target_rad, model_type)
            goal_addr = RX_ADDR_GOAL_POSITION if model_type == 28 else MX_ADDR_GOAL_POSITION
            try:
                self._write_2byte(
                    motor_id, goal_addr, goal_position, 'goal position write'
                )
            except RuntimeError as exc:
                self.get_logger().error(str(exc))

    def destroy_node(self):
        for motor_id, model_type in zip(self.motor_ids, self.model_types):
            torque_addr = (
                RX_ADDR_TORQUE_ENABLE if model_type == 28 else MX_ADDR_TORQUE_ENABLE
            )
            try:
                self._write_1byte(motor_id, torque_addr, TORQUE_DISABLE, 'torque disable')
            except RuntimeError as exc:
                self.get_logger().warn(str(exc))

        self.port_handler.closePort()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BaramGripperController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
