class TankMain:

    # import
    from evdev import InputDevice, categorize, ecodes
    import time as time
    from Chassis import Chassis
    from JsonHandler import JsonHandler
    import RPi.GPIO as GPIO

    class Axis:

        # Event_code: the event.code defining the axis.
        # The value from the event is ranged between 0 and 65568 we need
        # treshhold_max, treshhold_min and invert direction help translate that to -1, 0 and 1

        def __init__(self,
                     event_code,
                     treshhold_max,
                     treshhold_min,
                     invert_direction):

            self.treshhold_max = treshhold_max
            self.treshhold_min = treshhold_min
            self.event_code = event_code
            self.invert_direction = invert_direction
            self.current_value = 0

        def compare(self, event):
            return event.code == self.event_code

        def get_code(self):
            return self.event_code

        def get_direction(self, event):
            if event.value > self.treshhold_max:
                if self.invert_direction:
                    return -1
                else:
                    return 1
            elif event.value < self.treshhold_min:
                if self.invert_direction:
                    return 1
                else:
                    return -1
            else:
                return 0

    class Throttle:

        # Event_code: the event.code defining the throttle.
        # The value from the event is ranged between 0 and 256
        # treshhold_max helps translate that to 0 and 1

        def __init__(self,
                     event_code,
                     treshhold_max):

            self.treshhold_max = treshhold_max
            self.event_code = event_code

        def compare(self, event):
            return event.code == self.event_code

        def get_code(self):
            return self.event_code

        def get_value(self, event):
            if event.value > self.treshhold_max:
                return 1
            else:
                return 0

    # Variables
    continue_program = True
    x_direction = 0
    y_direction = 0
    right_throttle_value = 0
    left_throttle_value = 0

    def __init__(self):

        self.json_handler = self.JsonHandler()

        # set GPIO pins to Boardcom SOC channel numbering (defines how you refer to the pins)
        self.GPIO.setmode(self.GPIO.BCM)
        # GPIO 18 set up as input. It is pulled up to stop false signals
        self.GPIO.setup(self.json_handler.GPIO_stop_Button, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)

        # creates object 'gamepad' to store the data
        self.game_pad = self.InputDevice(self.json_handler.game_pad_input_device)

        # EV_ABS event.code 0: x axis left joystick
        self.x_axis = self.Axis(0, 55000, 15000, False)

        # EV_ABS event.code 1: y axis left joystick
        self.y_axis = self.Axis(1, 55000, 15000, True)

        # EV_ABS event.code 9: right throttle
        self.right_throttle = self.Throttle(9, 100)

        # EV_ABS event.code 10: left throttle
        self.left_throttle = self.Throttle(10, 100)

        # set timer of last event handling
        self.time_event_handling = self.time.time()
        self.time_to_sleep = 0.25

        # set the chassis
        self.chassis = self.Chassis(self.GPIO
                                    , self.json_handler.GPIO_in1
                                    , self.json_handler.GPIO_in2
                                    , self.json_handler.GPIO_ena
                                    , self.json_handler.GPIO_in3
                                    , self.json_handler.GPIO_in4
                                    , self.json_handler.GPIO_enb)

    def stop_button_pressed(self, channel):
        print("Stop button pressed")
        self.continue_program = False

    def set_new_direction(self, event):

        change_direction = False

        # Set the direction
        if self.y_axis.compare(event) and self.y_direction != self.y_axis.get_direction(event):
            self.y_direction = self.y_axis.get_direction(event)
            change_direction = True
        elif self.x_axis.compare(event) and self.x_direction != self.x_axis.get_direction(event):
            self.x_direction = self.x_axis.get_direction(event)
            change_direction = True

        if change_direction:
            # check if the command is not too fast. If is, wait
            if self.time.time() - self.time_event_handling < self.time_to_sleep:
                self.time.sleep(self.time_to_sleep)

            # set last time
            self.time_event_handling = self.time.time()

            # redirect
            if self.y_direction == 1 and self.x_direction == 0:
                self.chassis.go_forward()
            elif self.y_direction == 1 and self.x_direction == 1:
                self.chassis.turn_right()
            elif self.y_direction == 1 and self.x_direction == -1:
                self.chassis.turn_left()
            elif self.y_direction == -1 and self.x_direction == 0:
                self.chassis.go_backward()
            elif self.y_direction == 0 and self.x_direction == 1:
                self.chassis.turn_right_axis()
            elif self.y_direction == 0 and self.x_direction == -1:
                self.chassis.turn_left_axis()
            elif self.y_direction == 0 and self.x_direction == 0:
                self.chassis.stop()

    def set_new_gear(self, event):

        change_gear = False

        if self.right_throttle.compare(event) and self.right_throttle_value != self.right_throttle.get_value(event):
            self.right_throttle_value = self.right_throttle.get_value(event)
            change_gear = True
        elif self.left_throttle.compare(event) and self.left_throttle_value != self.left_throttle.get_value(event):
            self.left_throttle_value = self.left_throttle.get_value(event)
            change_gear = True

        if change_gear:
            # check if the command is not too fast. If is, wait
            if self.time.time() - self.time_event_handling < self.time_to_sleep:
                self.time.sleep(self.time_to_sleep)

            # set last time
            self.time_event_handling = self.time.time()

            # change gear
            if self.right_throttle_value == 1 and self.left_throttle_value == 0:
                self.chassis.gear_up()
                print("Gear UP")
            elif self.right_throttle_value == 0 and self.left_throttle_value == 1:
                self.chassis.gear_down()
                print("Gear DOWN")

    def is_throttle(self, event):
        return self.right_throttle.compare(event) or self.left_throttle.compare(event)

    def is_axis(self, event):
        return self.x_axis.compare(event) or self.y_axis.compare(event)

    def run_tank(self):

        self.GPIO.add_event_detect(self.json_handler.GPIO_stop_Button
                                   , self.GPIO.FALLING
                                   , callback=self.stop_button_pressed
                                   , bouncetime=200)
        print("start")

        # evdev takes care of polling the controller in a loop
        for event in self.game_pad.read_loop():
            # filters by event type
            if not self.continue_program:
                print("hier dus")
                break
            elif event.type == self.ecodes.EV_KEY and event.code == 308:  # "Y"
                break
            elif event.type == self.ecodes.EV_ABS:
                if self.is_axis(event):
                    self.set_new_direction(event)
                elif self.is_throttle(event):
                    self.set_new_gear(event)

        print("en hier")
        self.chassis.quit()
        self.GPIO.cleanup()


if __name__ == '__main__':
    tank = TankMain()
    tank.run_tank()