class Chassis:

    GPIO = None

    class Track:

        GPIO = None

        # define speeds
        duty_cycle_speed0 = 0
        duty_cycle_speed1 = 40
        duty_cycle_speed2 = 60
        duty_cycle_speed3 = 80
        duty_cycle_speed4 = 100
        # turn speed factor is used to hold a track in case of turing
        turn_speed_factor = 0.25
        # cruise speed factor is used when the chassis is going straight (so no turning)
        cruise_speed_factor = 1

        # define gears
        current_gear = 0
        gear_max = 4
        gear_min = 0
        speed_factor = cruise_speed_factor

        def __init__(self,
                     gpio,
                     gpio_motor_ina,
                     gpio_motor_inb,
                     gpio_motor_en):

            self.GPIO = gpio

            # initialize parameters
            self.gpio_motor_ina = gpio_motor_ina
            self.gpio_motor_inb = gpio_motor_inb
            self.gpio_motor_en = gpio_motor_en

            # set GPIO pins to Boardcom SOC channel numbering (defines how you refer to the pins)
            # is done by other class. self.GPIO.setmode(self.GPIO.BCM)

            # set up the PINS A motor needs three. "in A", "in B" and "ENable".
            # The enable enables the motor, the other two the direction (one low, one high. Both low means stop)
            self.GPIO.setup(self.gpio_motor_ina,
                            self.GPIO.OUT)
            self.GPIO.setup(self.gpio_motor_inb,
                            self.GPIO.OUT)
            self.GPIO.setup(self.gpio_motor_en,
                            self.GPIO.OUT)

            # Set the motor to "stop" or "stationary"
            self.GPIO.output(self.gpio_motor_ina,
                             self.GPIO.LOW)
            self.GPIO.output(self.gpio_motor_inb,
                             self.GPIO.LOW)

            # enable the motor, setting the duty cycle
            self.pwm = self.GPIO.PWM(self.gpio_motor_en,
                                     1000)
            self.pwm.start(self.duty_cycle_speed1)

        # Get methods
        def get_duty_cycle_speed(self, gear):
            # returns the duty_cycle setting corresponding to the given gear.
            # you can give a track a gear number from 0 - 4, which will be translated to a duty_cycle
            duty_cycle = 0
            if gear == 1:
                duty_cycle = self.duty_cycle_speed1
            elif gear == 2:
                duty_cycle = self.duty_cycle_speed2
            elif gear == 3:
                duty_cycle = self.duty_cycle_speed3
            elif gear == 4:
                duty_cycle = self.duty_cycle_speed4
            elif gear == 0:
                duty_cycle = self.duty_cycle_speed0
            return duty_cycle

        def get_gear(self):
            return self.current_gear

        # Set methods
        def set_cruise_speed(self):
            # set the factor, and recalculate the duty_cycle
            self.speed_factor = self.cruise_speed_factor
            self.set_duty_cycle()

        def set_duty_cycle(self, duty_cycle=None):
            # sets the GPIO duty_cycle based on given duty_cycle (from gear setting) and speed_factor (turn or cruise)
            # print(self.current_gear)
            new_duty_cycle = self.get_duty_cycle_speed(self.current_gear)
            if duty_cycle is not None:
                new_duty_cycle = duty_cycle
            # print(new_duty_cycle, self.speed_factor, new_duty_cycle * self.speed_factor)
            self.pwm.ChangeDutyCycle(int(new_duty_cycle * self.speed_factor))

        def set_gear(self, gear):
            duty_cycle_speed = self.get_duty_cycle_speed(gear)
            if duty_cycle_speed != 0:
                self.current_gear = gear
                self.set_duty_cycle(duty_cycle_speed)

        def set_turn_speed(self):
            # set the factor, and recalculate the duty_cycle
            self.speed_factor = self.turn_speed_factor
            self.set_duty_cycle()

        # Other methods
        def backward(self):
            # the motor is handled by 3 pins. inA and inB combined define the direction (one high, one low)
            self.GPIO.output(self.gpio_motor_ina,
                             self.GPIO.LOW)
            self.GPIO.output(self.gpio_motor_inb,
                             self.GPIO.HIGH)

        def forward(self):
            # the motor is handled by 3 pins. inA and inB combined define the direction (one high, one low)
            self.GPIO.output(self.gpio_motor_ina,
                             self.GPIO.HIGH)
            self.GPIO.output(self.gpio_motor_inb,
                             self.GPIO.LOW)

        def gear_down(self):
            if self.current_gear > self.gear_min:
                self.set_gear(self.current_gear - 1)
            else:
                self.set_gear(self.gear_min)

        def gear_up(self):
            if self.current_gear < self.gear_max:
                self.set_gear(self.current_gear + 1)
            else:
                self.set_gear(self.gear_max)

        def quit(self):
            # stop the motor
            self.pwm.ChangeDutyCycle(0)
            # clean up everything
            # self.GPIO.cleanup()

        def stop(self):
            # both IN pins low: stop
            self.GPIO.output(self.gpio_motor_ina,
                             self.GPIO.LOW)
            self.GPIO.output(self.gpio_motor_inb,
                             self.GPIO.LOW)
            self.set_gear(0)

    def __init__(self,
                 gpio,
                 gpio_motor_in1,
                 gpio_motor_in2,
                 gpio_motor_ena,
                 gpio_motor_in3,
                 gpio_motor_in4,
                 gpio_motor_enb):

        # set GPIO
        self.GPIO = gpio

        # define GPIO ports
        self.gpio_motor_in1 = gpio_motor_in1  # 24
        self.gpio_motor_in2 = gpio_motor_in2  # 23
        self.gpio_motor_ena = gpio_motor_ena  # 25
        self.gpio_motor_in3 = gpio_motor_in3  # 11
        self.gpio_motor_in4 = gpio_motor_in4  # 9
        self.gpio_motor_enb = gpio_motor_enb  # 10

        # define tracks
        self.leftTrack = self.Track(self.GPIO,
                                    self.gpio_motor_in3,
                                    self.gpio_motor_in4,
                                    self.gpio_motor_enb)
        self.rightTrack = self.Track(self.GPIO,
                                     self.gpio_motor_in1,
                                     self.gpio_motor_in2,
                                     self.gpio_motor_ena)

        self.ACTION_FORWARD = "ACTION FORWARD"
        self.ACTION_BACKWARD = "ACTION BACKWARD"
        self.ACTION_LEFT = "ACTION LEFT"
        self.ACTION_RIGHT = "ACTION RIGHT"
        self.ACTION_LEFT_AXIS = "ACTION LEFT AXIS"
        self.ACTION_RIGHT_AXIS = "ACTION RIGHT AXIS"
        self.ACTION_STOP = "ACTION RIGHT STOP"
        self.currentAction = self.ACTION_STOP

    def set_gear(self, gear):
        self.leftTrack.set_gear(gear)
        self.rightTrack.set_gear(gear)

    def gear_down(self):
        self.leftTrack.gear_down()
        self.rightTrack.gear_down()

    def gear_up(self):
        self.leftTrack.gear_up()
        self.rightTrack.gear_up()

    def go_backward(self):

        if self.currentAction == self.ACTION_BACKWARD:
            return

        self.currentAction = self.ACTION_BACKWARD

        # define the speed. Get the max of the tracks
        speed = max(self.leftTrack.current_gear, self.rightTrack.current_gear)
        speed = max(speed, 1)
        # set the gears of the tracks
        self.leftTrack.set_gear(speed)
        self.rightTrack.set_gear(speed)
        # set both tracks on cruising (turning is the other option)
        self.leftTrack.set_cruise_speed()
        self.rightTrack.set_cruise_speed()
        # Make it so!
        self.leftTrack.backward()
        self.rightTrack.backward()

    def go_forward(self):

        if self.currentAction == self.ACTION_FORWARD:
            return

        self.currentAction = self.ACTION_FORWARD

        # define the speed. Get the max of the tracks
        speed = max(self.leftTrack.current_gear, self.rightTrack.current_gear)
        speed = max(speed, 1)
        # set the gears of the tracks
        self.leftTrack.set_gear(speed)
        self.rightTrack.set_gear(speed)
        # set both tracks on cruising (turning is the other option)
        self.leftTrack.set_cruise_speed()
        self.rightTrack.set_cruise_speed()
        # Make it so!
        self.leftTrack.forward()
        self.rightTrack.forward()

    def quit(self):
        self.leftTrack.quit()
        self.rightTrack.quit()

    def stop(self):

        if self.currentAction == self.ACTION_STOP:
            return

        self.currentAction = self.ACTION_STOP

        self.leftTrack.stop()
        self.rightTrack.stop()

    def turn_left(self):

        if self.currentAction == self.ACTION_LEFT:
            return

        self.currentAction = self.ACTION_LEFT

        # left must be slower than right
        self.leftTrack.set_turn_speed()
        self.rightTrack.set_cruise_speed()

    def turn_left_axis(self):

        if self.currentAction == self.ACTION_LEFT_AXIS:
            return

        self.currentAction = self.ACTION_LEFT_AXIS

        self.leftTrack.set_gear(2)
        self.rightTrack.set_gear(2)
        self.leftTrack.backward()
        self.rightTrack.forward()

    def turn_right(self):

        if self.currentAction == self.ACTION_RIGHT:
            return

        self.currentAction = self.ACTION_RIGHT

        # right must be slower than left
        self.leftTrack.set_cruise_speed()
        self.rightTrack.set_turn_speed()

    def turn_right_axis(self):

        if self.currentAction == self.ACTION_RIGHT_AXIS:
            return

        self.currentAction = self.ACTION_RIGHT_AXIS

        self.leftTrack.set_gear(2)
        self.rightTrack.set_gear(2)
        self.leftTrack.forward()
        self.rightTrack.backward()

