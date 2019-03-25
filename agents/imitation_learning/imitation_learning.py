import carla 
from agents.navigation.agent import *
from agents.navigation.local_planner import LocalPlanner
from agents.navigation.local_planner import compute_connection, RoadOption

from agents.tools.misc import get_speed

from keras.models import load_model

import numpy as np

import agents.imitation_learning.utils as utils

class ImitationLearning(Agent):
    """
    RoamingAgent implements a basic agent that navigates scenes making random
    choices when facing an intersection.

    This agent respects traffic lights and other vehicles.
    """

    def __init__(self, vehicle):
        """

        :param vehicle: actor to apply to local planner logic onto
        """
        super(ImitationLearning, self).__init__(vehicle)
        self._proximity_threshold = 10.0  # meters
        self._state = AgentState.NAVIGATING
        self._local_planner = LocalPlanner(self._vehicle)
        self.model = load_model('pre-trained_model/experiment04/model-003.h5')


        # setting up global router
        self._current_plan = None

        self._image = None

    def set_image(self, image):
        self._image = image

    def set_destination(self, location):
        start_waypoint = self._map.get_waypoint(self._vehicle.get_location())
        end_waypoint = self._map.get_waypoint(carla.Location(location[0],
                                                             location[1],
                                                             location[2]))

        current_waypoint = start_waypoint
        active_list = [ [(current_waypoint, RoadOption.LANEFOLLOW)] ]

        solution = []
        while not solution:
            for _ in range(len(active_list)):
                trajectory = active_list.pop()
                if len(trajectory) > 1000:
                    continue

                # expand this trajectory
                current_waypoint, _ = trajectory[-1]
                next_waypoints = current_waypoint.next(5.0)
                while len(next_waypoints) == 1:
                    next_option = compute_connection(current_waypoint, next_waypoints[0])
                    current_distance = next_waypoints[0].transform.location.distance(end_waypoint.transform.location)
                    if current_distance < 5.0:
                        solution = trajectory + [(end_waypoint, RoadOption.LANEFOLLOW)]
                        break

                    # keep adding nodes
                    trajectory.append((next_waypoints[0], next_option))
                    current_waypoint, _ = trajectory[-1]
                    next_waypoints = current_waypoint.next(5.0)

                if not solution:
                    # multiple choices
                    for waypoint in next_waypoints:
                        next_option = compute_connection(current_waypoint, waypoint)
                        active_list.append(trajectory + [(waypoint, next_option)])

        assert solution

        self._current_plan = solution
        self._local_planner.set_global_plan(self._current_plan)

    def run_step(self, debug=False):
        """
        Execute one step of navigation.
        :return: carla.VehicleControl
        """

        # is there an obstacle in front of us?
        hazard_detected = False

        # retrieve relevant elements for safe navigation, i.e.: traffic lights
        # and other vehicles
        # actor_list = self._world.get_actors()
        # vehicle_list = actor_list.filter("*vehicle*")
        # lights_list = actor_list.filter("*traffic_light*")

        # # check possible obstacles
        # vehicle_state, vehicle = self._is_vehicle_hazard(vehicle_list)
        # if vehicle_state:
        #     if debug:
        #         print('!!! VEHICLE BLOCKING AHEAD [{}])'.format(vehicle.id))

        #     self._state = AgentState.BLOCKED_BY_VEHICLE
        #     hazard_detected = True

        # # check for the state of the traffic lights
        # light_state, traffic_light = self._is_light_red(lights_list)
        # if light_state:
        #     if debug:
        #         print('=== RED LIGHT AHEAD [{}])'.format(traffic_light.id))

        #     self._state = AgentState.BLOCKED_RED_LIGHT
        #     hazard_detected = True

        if hazard_detected:
            control = self.emergency_stop()
            high_level_command = RoadOption.VOID
        else:
            self._state = AgentState.NAVIGATING
            # standard local planner behavior
            _, high_level_command = self._local_planner.run_step(debug=debug)
            print(high_level_command)
            control = self._compute_action(self._image, get_speed(self._vehicle), high_level_command.value)

        return control

    def _compute_action(self, rgb_image, speed, direction=None):

        image_input = rgb_image
        image_input = utils.preprocess(image_input)
        image_input = image_input.astype(np.float32)
        image_input = np.multiply(image_input, 1.0 / 255.0)

        steer, acc, brake = self._control_function(image_input, speed, direction)

        # This a bit biased, but is to avoid fake breaking

        if brake < 0.1:
            brake = 0.0

        if acc > brake:
            brake = 0.0

        # We limit speed to 35 km/h to avoid
        if speed > 10.0 and brake == 0.0:
            acc = 0.0

        control = carla.VehicleControl()
        control.steer = steer / 0.25
        control.throttle = acc / 0.25
        control.brake = brake / 0.25

        control.hand_brake = False

        return control

    def _control_function(self, image, speed, direction):
        try:
            # image = utils.preprocess(image) # apply the preprocessing
            image = np.array([image])       # the model expects 4D array
            
            speed = np.array([speed/100])

            direction = np.array([direction/10])
            predict_data = self.model.predict([image, speed, direction], batch_size=1)
            predicted_acc, predicted_steers, predicted_brake = predict_data[0]

            return float(predicted_steers), float(predicted_acc), float(predicted_brake)



        except Exception as e:
            print(e)

        return 0, 0, 0
