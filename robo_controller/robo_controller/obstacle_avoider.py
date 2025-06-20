import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        self.publisher_ = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.listener_callback,
            10)
        self.get_logger().info('Obstacle Avoider node has been started.')


    def listener_callback(self, msg):
        # We check a range of points in front of the robot for robustness
        # The front is 0 degrees, let's check +/- 10 degrees
        front_slice = msg.ranges[350:] + msg.ranges[:11]
        min_front_distance = min(front_slice)
        
        # Create a TwistStamped message
        move_cmd = TwistStamped()

        # CRITICAL: Fill the header with the current time. This is what was missing.
        move_cmd.header.stamp = self.get_clock().now().to_msg()
        
        # The velocity commands now go inside the 'twist' field of the message
        if min_front_distance > 0.5:
            self.get_logger().info(f'Path is clear (distance: {min_front_distance:.2f}m), moving forward.')
            move_cmd.twist.linear.x = 0.2  # m/s
            move_cmd.twist.angular.z = 0.0 # rad/s
        else:
            self.get_logger().info(f'Obstacle detected at {min_front_distance:.2f}m! Turning.')
            move_cmd.twist.linear.x = 0.0
            move_cmd.twist.angular.z = 0.5 # rad/s
        
        self.publisher_.publish(move_cmd)
        
        
def main(args=None):
    rclpy.init(args=args)
    obstacle_avoider = ObstacleAvoider()
    rclpy.spin(obstacle_avoider)
    obstacle_avoider.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
