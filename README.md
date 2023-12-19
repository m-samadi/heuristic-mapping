# Heuristic task-to-thread mapping
This program simulates task-to-thread mapping for OpenMP applications based on several heuristics.
<br/>
<br/>
## Version
The simulator includes two versions, but the results are produced based on the first version. However, there are not many changes in the second version, just a few (e.g., renaming the parameters).
<br/>
<br/>
Furthermore, each version is developed with/without overhead. The code with overhead is written based on threads (to emulate the simulation like the implementation), while the code without overhead is written based on loop.
<br/>
<br/>
## Simulation parameters
The simulation parameters are set by default. Therefore, they can be modified at the beginning of main.py based on application requirements.
<br/>
<br/>
## Graphical output
If it is needed to produce graphical outputs at the end of the simulation, set the variable ‘graphic_result’ to 1. Note that there is a limitation in drawing the shapes in Python. Therefore, if number of tasks is many, keep it disabled.
<br/>
<br/>
## Run
The simulation is run on each version using the following command:
```
python main.py
```
If the DAG is generated based on a predefined graph (i.e., benchmark), press 'y'; unless press 'n'.
