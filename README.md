# Hungry-Bots
Using a genetic algorithm to train feedforward neural networks with a fun visual.

In this script, bots (colored circles) must eat food (collide with small white dots) to continue to survive. The fitness function is directly related to the number of sprite engine updates a bot "lives" through. Here are the bots when the script first begins. They do not seek out food, so the die and disappear.

<img src="https://raw.githubusercontent.com/CharlesOB/Hungry-Bots/main/Screen Capture 1.gif" height="540" width="950">



After they have trained for five to ten minutes, the bots already display "intelligent" behavior, spotting food and moving towards it. Some bots still struggle--this is often the result of random mutation, a necessary component of a genetic algorithm.

<img src="https://raw.githubusercontent.com/CharlesOB/Hungry-Bots/main/Screen Capture 2.gif" height="540" width = "950">

## Execution
The script uses Python 3 with numpy and pygame installed using `pip`.
```
pip3 install numpy pygame
```
Running the script is as simple as
```
python3 hungry_bots.py
```
Have fun watching your little bots learn!
