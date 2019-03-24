import csv
import datetime
import os
import scipy
from agents.navigation.local_planner import RoadOption

"""
----------------------
High Level Command
---------------------- 
VOID = -1
LEFT = 1
RIGHT = 2
STRAIGHT = 3
LANEFOLLOW = 4
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
            'high_level_command': -1
        }

        # Just in the case is the first time and there is no benchmark results folder
        if not os.path.exists('_out'):
            os.mkdir('_out')

        # Generate the full path for the log files
        self._path = os.path.join('_out', name_to_save)

        self.count = {
            'left': 0,
            'right': 0,
            'straight': 0,
            'lanefollow': 0,
            'void': 0
        }

        self.left_count = 0
        self.right_count = 0
        self.straight_count = 0

        self.is_left_finish = False
        self.is_right_finish = False
        self.is_straight_finish = False
        self.is_lanefollow_finish = False

    @property
    def path(self):
        return self._path

    def check_image_count(self):
        if self.count['left'] >= 10000 and self.count['right'] >= 10000 and self.count['straight'] >= 10000 and self.count['lanefollow'] >= 10000:
            return True
        return False

    def save_to_csv(self, frame_number, image, measurements, high_level_command):
        """Write all neccesary data to csv file"""

        if (self.check_image_count()):
            print('Finish Successful!')
            quit(0)

        if high_level_command.value == 1:
            if self.count['left'] > 10000:
                if self.is_left_finish == False:
                    print('left finish!')
                self.is_left_finish = True
                return 
            image_path = os.path.join(self.path, 'left')
            self.count['left'] += 1
            self.left_count += 1

        elif high_level_command.value == 2:
            if self.count['right'] > 10000:
                if self.is_right_finish == False:
                    print('right finish!')
                self.is_right_finish = True
                return 
            image_path = os.path.join(self.path, 'right')
            self.count['right'] += 1
            self.right_count += 1
        
        elif high_level_command.value == 3:
            if self.count['straight'] > 10000:
                if self.is_straight_finish == False:
                    print('straight finish!')
                self.is_straight_finish = True
                return 
            image_path = os.path.join(self.path, 'straight')
            self.count['straight'] += 1
            self.straight_count += 1

        elif high_level_command.value == 4:
            if self.count['lanefollow'] > 10000:
                if self.is_lanefollow_finish == False:
                    print('lanefollow finish!')
                self.is_lanefollow_finish = True
                if self.left_count <= 100 and self.left_count > 0:
                    image_path = os.path.join(self.path, 'left')
                    self.count['left'] += 1
                    self.left_count += 1
                    high_level_command = RoadOption.LEFT
                elif self.right_count <= 100 and self.right_count > 0:
                    image_path = os.path.join(self.path, 'right')
                    self.count['right'] += 1
                    self.right_count += 1
                    high_level_command = RoadOption.RIGHT
                elif self.straight_count <= 100 and self.straight_count > 0:
                    image_path = os.path.join(self.path, 'straight')
                    self.count['straight'] += 1
                    self.straight_count += 1
                    high_level_command = RoadOption.STRAIGHT
                else:
                    self.left_count = 0
                    self.right_count = 0
                    return   
            else:
                image_path = os.path.join(self.path, 'lanefollow')
                if self.left_count <= 100 and self.left_count > 0:
                    image_path = os.path.join(self.path, 'left')
                    self.count['left'] += 1
                    self.left_count += 1
                elif self.right_count <= 100 and self.right_count > 0:
                    image_path = os.path.join(self.path, 'right')
                    self.count['right'] += 1
                    self.right_count += 1
                elif self.straight_count <= 100 and self.straight_count > 0:
                    image_path = os.path.join(self.path, 'straight')
                    self.count['straight'] += 1
                    self.straight_count += 1
                else:
                    self.left_count = 0
                    self.right_count = 0
                    self.count['lanefollow'] += 1
        else:
            if self.count['void'] > 10000:
                print('void finish!', end='\r')
                return 
            image_path = os.path.join(self.path, 'void')
            self.count['void'] += 1

        image_path = os.path.join(image_path, 'images/%09d.jpg' % frame_number)
        image.save_to_disk(image_path)

        self._dict['frame'] = frame_number
        self._dict['image_path'] = image_path
        self._dict['throttle'] = measurements['throttle']
        self._dict['steering_angle'] = measurements['steer']
        self._dict['brake'] = measurements['brake']
        self._dict['speed'] = measurements['speed']
        self._dict['high_level_command'] = high_level_command.value

        with open(self.path + '/data.csv', 'a', newline='') as csvfile:
            fieldnames = [
                'frame',
                'image_path',
                'throttle',
                'steering_angle',
                'brake',
                'speed',
                'high_level_command'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only for the first frame
            if frame_number == 0:
                writer.writeheader()

            writer.writerow(self._dict)
