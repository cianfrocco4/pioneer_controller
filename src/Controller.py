#!/usr/bin/env python3

import termios, fcntl, sys, os, rospy, roslib
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Point
from p2os_msgs.msg import MotorState

class Controller:
    __slots__ = ['commandVelocityPublisher', "commandMotorStatePublisher"]

    def __init__(self):
        rospy.init_node('controller')
        #self.commandVelocityPublisher = rospy.Publisher('mobile_base/commands/velocity', Twist)
        self.commandVelocityPublisher = rospy.Publisher('/cmd_vel', Twist)
        self.commandMotorStatePublisher = rospy.Publisher('/cmd_motor_state', MotorState, latch=True)

    def run(self):
        fd = sys.stdin.fileno()
    
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        speed = .1

        motorState = MotorState()
        motorState.state = 1
        self.commandMotorStatePublisher.publish(motorState)

        print('Set motor state to 1')

        try:
            twist = Twist()
            while True:
                try:
                    c = sys.stdin.read(1)
                    if c == '\x1b':
                        c = sys.stdin.read(2)
                    if c == '[A' or c == 'w':
                        print('move forward %5.2f m/s' % (speed))
                        twist.linear.x = speed
                    elif c == '[C' or c == 'd':
                        print('rotate right .5 m/s')
                        twist.angular.z = -0.5
                    elif c == '[D' or c == 'a':
                        print('rotate left .5 m/s')
                        twist.angular.z = 0.5
                    elif c == '-':
                        speed = max(.1, speed - .1)
                        print('decreasing linear speed to ', speed)
                    elif c == '+':
                        speed = min(.5, speed + .1)
                        print ('increasing linear speed to ', speed)
                    elif c == 'q':
                        twist = Twist()
                        self.commandVelocityPublisher.publish(twist)
                        return
                    elif c == 's':
                        twist = Twist()
                        print('stopping motion')
                    elif c == 'x':
                        twist.linear.x = -speed
                        print('move backward %5.2f m/s' % (-speed))
                    elif False:
                        print ('Controls:')
                        print ('          w or up    : move forward')
                        print ('          a or left  : rotate counterclockwise')
                        print ('          d or right : rotate clockwise')
                        print ('          -          : decrease linear speed by .1 m/s (.1 m/s minimum)')
                        print ('          +          : increase linear speed by .1 m/s (.5 m/s maximum)')
                        print ('          q          : quit')
                    #more seamless with multiple requests
                    self.commandVelocityPublisher.publish(twist)
                    self.commandVelocityPublisher.publish(twist)
                    self.commandVelocityPublisher.publish(twist)
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags) 

if __name__=='__main__':
    Controller().run()
