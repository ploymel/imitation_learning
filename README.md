# Self driving with simulator
This respository was created for the senior project of our Bachelor's Degree in Computer Science.<br/>  
This project is focusing on prediction the car behaviour using Conditional Imitation Learning.<br/>  
For the network that we used in this project we modified from [End-to-end Driving via Conditional Imitation Learning](http://vladlen.info/papers/conditional-imitation.pdf)<br/>  

**Note:** All data in our dataset collected from simulator [CARLA](http://carla.org/)<br/> 

## Getting Started
**CARLA Simulator**<br/>
- Please following the installation in: [CARLA Documentation](https://carla.readthedocs.io/en/latest/)<br/>

**Clone this repository**<br/>
```
git clone https://github.com/ploymel/imitation_learning.git
```

**Note:** For the other necsssary agents source code of this project please refer to: [carla agents API github](https://github.com/carla-simulator/carla/tree/master/PythonAPI/agents)<br/>

## Requirements
- tensorflow_gpu 1.1 or more
- Keras
- numpy
- scipy
- PIL
- Jupyter Notebook

## Running
**Collect data**<br/>
```
$ python drive.py
```
After the program running press `R` to start Recording.<br/>

**Training Model**
The training files are in `models/experiment**` folder
```
# open jupyter notebook
$ jupyter notebook
```

**Testing**
- Open the simulator
- Run the following command
```
$ python drive.py -a Imitaion
```

## Dataset
- [The dataset for the first pharse - no obstacles and traffic lights can be download here](https://drive.google.com/file/d/1s5NGfWNNpd7b1EYixHStOhw4R7BqTWU8/view?usp=sharing) 1.6 GB

The data is stored on CSV file. The CSV contains 7 columns:<br/>
1. frame (Frame number)
2. image path (The RGB images stored at 200x66 resolution)
3. throttle, float
4. steering_angle, float
5. brake, float
6. speed, float
7. high_level_command, float (which 1.0, 2.0, 3.0 and 4.0 are represented left, right, straight and lanefollow.)

## Preprocess
See [data_augmetation.ipynb](https://github.com/ploymel/imitation_learning/blob/master/augmentation/data_augmentation.ipynb) for more information.

## Neural Network
![Neural Network](img/network.png)


## References
- [End-to-end Driving via Conditional Imitation Learning](http://vladlen.info/papers/conditional-imitation.pdf)<br/>
Codevilla, Felipe and Müller, Matthias and López, Antonio and Koltun, Vladlen and Dosovitskiy, Alexey. ICRA 2018
- [End to End Learning for Self-Driving Cars](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf)<br/>
Nvidia

