import carla 
from agents.navigation.agent import *
from agents.navigation.local_planner import LocalPlanner
from agents.navigation.local_planner import compute_connection, RoadOption

from agents.tools.misc import get_speed

from keras.models import load_model

import numpy as np

import agents.imitation.image_utils as utils
import math

class ImitationAgent(Agent):
    """
    RoamingAgent implements a basic agent that navigates scenes making random
    choices when facing an intersection.

    This agent respects traffic lights and other vehicles.
    """

    def __init__(self, vehicle, model_path):
        """

        :param vehicle: actor to apply to local planner logic onto
        """
        super(ImitationAgent, self).__init__(vehicle)
        self._proximity_threshold = 10.0  # meters
        self._state = AgentState.NAVIGATING
        self._local_planner = LocalPlanner(self._vehicle)
        self.model = load_model("pre-trained/" + model_path)

        # setting up global router
        self._current_plan = None

        self._image = None
        self._command = -1
        self._traffic_state = 0

    def set_image(self, image):
        self._image = image

    def set_traffic_state(self, traffic_state):
        if traffic_state == 2 or traffic_state == 1: # stop
            self._traffic_state = 0
        else: # go
            self._traffic_state = 1

    def set_command(self, command):
        self._command = command

    def run_step(self, debug=False):
        """
        Execute one step of navigation.
        :return: carla.VehicleControl
        """
        control = self._compute_action(self._image, get_speed(self._vehicle), self._traffic_state, self._command)

        return control, self._command

    def _compute_action(self, rgb_image, speed, traffic_state, direction=None):

        image_input = rgb_image
        image_input = image_input.astype(np.float32)

        steer, acc, brake = self._control_function(image_input, speed, traffic_state, direction)

        # This a bit biased, but is to avoid fake breaking

        if brake < 0.1:
            brake = 0.0

        if acc > brake:
            brake = 0.0

        # We limit speed to 20 km/h to avoid
        if speed > 20.0 and brake == 0.0:
            acc = 0.0

        control = carla.VehicleControl()
        control.steer = steer
        control.throttle = acc
        control.brake = brake

        cmd = ''
        if direction == 1:
            cmd = 'turn left'
        elif direction == 2:
            cmd = 'turn right'
        elif direction == 3:
            cmd = 'go straight'
        else:
            cmd = 'follow the lane'

        tl = ''
        if traffic_state == 0:
            tl = 'stop!'
        else:
            tl = 'go!'

        print(cmd, tl)

        control.hand_brake = False


        return control

    def encode_direction(self, direction):
        cmd = [0, 0, 0, 0]
        if direction == 4:
            cmd[0] = 1
        elif direction == 3:
            cmd[1] = 1
        elif direction == 2:
            cmd[2] = 1
        else:
            cmd[3] = 1
        return cmd


    def _control_function(self, image, speed, traffic_state, direction):
        try:
            image = utils.resize(image)

            cmd = self.encode_direction(direction)

            image = np.array([image])
            speed = np.array([speed/20])
            tl = np.array([traffic_state])
            cmd = np.array([cmd])
            
            predict_data = self.model.predict([image, speed, tl, cmd], batch_size=1)
            predicted_acc, predicted_steers, predicted_brake = predict_data[0]

            return float(predicted_steers), float(predicted_acc), float(predicted_brake)



        except Exception as e:
            print(e)

        return 0, 0, 0