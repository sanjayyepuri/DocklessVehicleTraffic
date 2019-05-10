# AI Project: Austin Traffic 

## Download the following files to the data folder. 

### Volume data 
Link to dataset source:
https://data.austintexas.gov/Transportation-and-Mobility/Traffic-Studies-Vehicle-Volume-Reports-BETA-/jasf-x4rx
Download link:
https://data.austintexas.gov/api/views/jasf-x4rx/rows.csv?accessType=DOWNLOAD

### Location data
Link to dataset source:
https://data.austintexas.gov/Transportation-and-Mobility/Traffic-Studies-Locations-BETA-/jqhg-imb3
Download link:
https://data.austintexas.gov/api/views/jqhg-imb3/rows.csv?accessType=DOWNLOAD

## Running the notebook
Make sure you have Docker installed and running. Then change the path to this repository in `start_docker.sh` and run the script. 


## Important Files 
Loading, cleaning and prepping the data for the bayesion network can be found in `dockless_data.py`. The code for the bayesian network and learning the conditional probablities as well as sampling are in `dockless_model.py`. The simulator that computes the paths and stores the frequencies in a networkx graph is found in `simluator.py`. 

The notebooks `DocklessScooterBayes.ipynb` and `DocklessScooterBayes[Prototype].ipynb` detail how we experiemented and created the bayes net. 


