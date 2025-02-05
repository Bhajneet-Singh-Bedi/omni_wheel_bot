# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# For remapping.
# ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=my_cmd_vel 
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import time

class VelocityTestNode(Node):
    def __init__(self):
        super().__init__('omni_wheel_bot_node')
        self.subscription = self.create_subscription(JointState, 'joint_states', self.velocity_listener_callback, 5)
        self.get_logger().info('Node created')


    def velocity_listener_callback(self, msg):
        self.get_logger().info('Message '+ str(msg.position[0]))
               


    
def main(args=None):
    rclpy.init(args=args)

    node = VelocityTestNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()