import json as json


class JsonHandler:

    def __init__(self):

        with open("init.json") as jsonFile:
            init_info = json.load(jsonFile)
            jsonFile.close()

            self.game_pad_input_device = init_info['InputDevice']['gamePad input device']
            self.GPIO_stop_Button = init_info['GPIO interface']['Stop button']
            self.GPIO_in1 = init_info['GPIO motors']['Motor 1 in1']
            self.GPIO_in2 = init_info['GPIO motors']['Motor 1 in2']
            self.GPIO_ena = init_info['GPIO motors']['Motor 1 enable']
            self.GPIO_in3 = init_info['GPIO motors']['Motor 2 in1']
            self.GPIO_in4 = init_info['GPIO motors']['Motor 2 in2']
            self.GPIO_enb = init_info['GPIO motors']['Motor 2 enable']
            self.GPIO_trigger = init_info['GPIO ultrasound sensor']['Trigger']
            self.GPIO_echo = init_info['GPIO ultrasound sensor']['Echo']
            self.GPIO_green_LED = init_info['GPIO interface']['Green LED']
            self.cruise_speed_factor = init_info['Speed setup']['Cruise speed factor']
            self.turn_speed_factor = init_info['Speed setup']['Turn speed factor']
            self.auto_cruise_speed = init_info['Speed setup']['Auto cruise speed']

    def print_settings(self):
        print("GamePadDevice: " + self.game_pad_input_device)
        print("Stop Button GPIO: " + str(self.GPIO_stop_Button))
        print("Motor 1 in1: " + str(self.GPIO_in1))
        print("Motor 1 in2: " + str(self.GPIO_in2))
        print("Motor 1 enable: " + str(self.GPIO_ena))
        print("Motor 2 in1: " + str(self.GPIO_in3))
        print("Motor 2 in2: " + str(self.GPIO_in4))
        print("Motor 2 enable: " + str(self.GPIO_enb))
        print("Ultrasound trigger: " + str(self.GPIO_trigger))
        print("Ultrasound echo: " + str(self.GPIO_echo))
        print("Green led: " + str(self.GPIO_green_LED))
        print("Cruise speed factor: " + str(self.cruise_speed_factor))
        print("Turn speed factor: " + str(self.turn_speed_factor))
        print("Auto cruise speed: " + str(self.auto_cruise_speed))


if __name__ == '__main__':
    jsonHandler = JsonHandler()
    jsonHandler.print_settings()
