import csv
import datetime
import os
import scipy


"""
----------------------
High Level Command
---------------------- 
VOID = -1
LEFT = 1
RIGHT = 2
STRAIGHT = 3
LANEFOLLOW = 4

----------------------
TrafficLightState
----------------------

NOTRAFFIC = 0
RED = 1
YELLOW = 2
GREEN = 3
"""

class Recording(object):

    def __init__(self, name_to_save):
        self._dict = {
            'frame': 0,
            'image_path': '',
            'throttle': 0.0,
            'steering_angle': 0.0,
            'brake': 0.0,
            'speed': 0.0,
            'traffc_state': 0,
            'high_level_command': -1
        }

        # Just in the case is the first time and there is no benchmark results folder
        if not os.path.exists('_out'):
            os.mkdir('_out')

        # Generate the full path for the log files
        self._path = os.path.join('_out', name_to_save)

    @property
    def path(self):
        return self._path

    def save_to_csv(self, frame_number, image, measurements, high_level_command, episode, frame, traffic_state):
        """Write all neccesary data to csv file"""

        image_path = os.path.join(self.path, 'images', '%02d' % episode, '%09d.jpg' % frame_number)
        image.save_to_disk(image_path)

        self._dict['frame'] = frame
        self._dict['image_path'] = image_path
        self._dict['throttle'] = measurements['throttle']
        self._dict['steering_angle'] = measurements['steer']
        self._dict['brake'] = measurements['brake']
        self._dict['speed'] = measurements['speed']
        self._dict['traffic_state'] = traffic_state
        self._dict['high_level_command'] = high_level_command

        with open(self.path + '/data.csv', 'a', newline='') as csvfile:
            fieldnames = [
                'frame',
                'image_path',
                'throttle',
                'steering_angle',
                'brake',
                'speed',
                'traffic_state',
                'high_level_command'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only for the first frame
            if frame_number == 0:
                writer.writeheader()

            writer.writerow(self._dict)
