class AutoTank:

    # import
    import RPi.GPIO as GPIO
    import time
    import threading
    from Chassis import Chassis
    from JsonHandler import JsonHandler

    # variable
    continue_program = True

    class GreenLED(threading.Thread):

        # This class gets its own thread.

        # Declarations
        GPIO = None
        GPIO_green_LED = None
        time = None
        sleep_time = 0.5
        running = True

        def __init__(self, GPIO, threading, time, GPIO_green_LED, name, thread_id):
            # set all variables
            self.threading = threading
            self.GPIO = GPIO
            self.time = time

            # Set GPIO pins
            self.GPIO_green_LED = GPIO_green_LED
            self.GPIO.setup(self.GPIO_green_LED, self.GPIO.OUT)

            # initialize thread
            self.threading.Thread.__init__(self)
            self.threadID = thread_id
            self.name = name

        @staticmethod
        def calc_sleep_time(dist):

            calc_dist = 1
            if dist > 100:
                calc_dist = 100
            elif dist > 1:
                calc_dist = dist

            sleep_time = 2 * pow(0.8, (110 - calc_dist) / 10)

            return sleep_time

        def run(self):
            # Running the blinking light
            print("Starting " + self.name)
            while self.running:
                self.GPIO.output(self.GPIO_green_LED, self.GPIO.HIGH)
                self.time.sleep(self.sleep_time)
                self.GPIO.output(self.GPIO_green_LED, self.GPIO.LOW)
                self.time.sleep(self.sleep_time)
                print("sleep time = %.1f" % self.sleep_time)

        def set_blink_speed(self, dist):
            self.set_sleep_time(self.calc_sleep_time(dist))

        def set_sleep_time(self, sleep_time):
            # set the time between LED on and LED off
            self.sleep_time = sleep_time

        def terminate(self):
            # termination of the thread
            self.running = False

    def __init__(self):

        self.json_handler = self.JsonHandler()

        # set GPIO pins to Boardcom SOC channel numbering (defines how you refer to the pins)
        self.GPIO.setmode(self.GPIO.BCM)

        # set GPIO Pins
        self.GPIO_trigger = self.json_handler.GPIO_trigger
        self.GPIO_echo = self.json_handler.GPIO_echo
        self.GPIO_green_led = self.json_handler.GPIO_green_LED

        # set GPIO direction (IN / OUT)
        self.GPIO.setup(self.GPIO_trigger, self.GPIO.OUT)
        self.GPIO.setup(self.GPIO_echo, self.GPIO.IN)

        # GPIO 18 set up as input. It is pulled up to stop false signals
        self.GPIO.setup(self.json_handler.GPIO_stop_Button, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)

        # set the chassis
        self.chassis = self.Chassis(self.GPIO
                                    , self.json_handler.GPIO_in1
                                    , self.json_handler.GPIO_in2
                                    , self.json_handler.GPIO_ena
                                    , self.json_handler.GPIO_in3
                                    , self.json_handler.GPIO_in4
                                    , self.json_handler.GPIO_enb)

        #set the lights
        self.thread_green_led = self.GreenLED(self.GPIO
                                              , self.threading
                                              , self.time
                                              , self.GPIO_green_led
                                              , "Thread-1"
                                              , 1)

    def distance(self):

        # set Trigger to HIGH
        self.GPIO.output(self.GPIO_trigger, True)

        # set Trigger after 0.01ms to LOW
        self.time.sleep(0.00001)
        self.GPIO.output(self.GPIO_trigger, False)

        start_time = self.time.time()
        stop_time = self.time.time()

        # save StartTime
        while self.GPIO.input(self.GPIO_echo) == 0:
            start_time = self.time.time()

        # save time of arrival
        while self.GPIO.input(self.GPIO_echo) == 1:
            stop_time = self.time.time()

        # time difference between start and arrival
        time_elapsed = stop_time - start_time

        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2

        return distance

    def find_way(self):

        # determine distance
        dist = self.distance()

        while dist < 40:
            dist = self.distance()
            self.chassis.go_backward()

        self.chassis.stop()

        while dist < 60:
            self.chassis.turn_left_axis()
            self.time.sleep(1)
            self.chassis.stop()
            dist = self.distance()
            self.time.sleep(0.5)

    def drive(self):

        while self.continue_program:

            # determine distance
            dist = self.distance()

            # drive
            if dist < 30:
                self.chassis.stop()
                self.find_way()
            elif dist > 40:
                self.chassis.go_forward()

            # set blinking light
            self.thread_green_led.set_blink_speed(dist)

            print("Measured Distance = %.1f cm" % dist)
            self.time.sleep(1)

    def run_tank_on_auto(self):

        try:
            self.chassis.set_gear(2)
            self.GPIO.add_event_detect(self.json_handler.GPIO_stop_Button
                                       , self.GPIO.FALLING
                                       , callback=self.stop_button_pressed
                                       , bouncetime=200)

            print("start")
            self.thread_green_led.start()
            self.drive()

        except KeyboardInterrupt:
            print("Measurement stopped by User")

        finally:
            print("Stopping programm")
            self.thread_green_led.terminate()
            while self.thread_green_led.is_alive():
                 niks = 0
            print("Ended threads")
            self.GPIO.cleanup()

    def stop_button_pressed(self, channel):
        print("Stop button pressed")
        self.continue_program = False


if __name__ == '__main__':
    autoTank = AutoTank()
    autoTank.run_tank_on_auto()
