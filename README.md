# Protocol_SMS_CrossCultural_2025
 
 ## TO DO
 
 - [ ] Create a file with the required libraries

This repository contains the experimental code used to investigate sensorimotor synchronization mechanisms of frequency adaptation, comparing French and Indian participants.

## Project Structure

The project is organized into the following directories:

### data/
Contains participant csv files of the preferred frequency measurements. Each participant should have their own subdirectory.

Expected file naming convention:
- `participantID_Pref__trialNb.csv`

Note: The data directory is initially empty. Create individual participant folders as you conduct the experiment.

### src/
Contains Python source files with functions used throughout the experiment. These functions support various experimental tasks and data collection processes.

### notebooks/
Contains three Jupyter notebooks that are essential for running the experiment:

- `randomization.ipynb`: Handles randomization procedures for the experiment
- `calculate_preferred_freq.ipynb`: Processes and calculates preferred frequencies
- `generate_stimuli.ipynb`: Creates stimuli based on experimental parameters

Note: These notebooks utilize functions from the src/ directory.

## Getting Started

1. Ensure you have all required dependencies installed
2. Create a participant folder in the data directory for each new participant
3. Execute the notebooks in the following order:
   - Randomization
   - Preferred Frequency Calculator
   - Stimuli Generator

## Data Structure

Each participant's data will be stored in CSV format with the following naming convention:
`participantID_Pref__trialNb.csv`

## eLabFTW Integration

The codebas includes optional integration with eLabFTW through its API. This functionality allows direct data transfer to eLabFTW but is not required to run the experiment. To disable this feature, simply remove the `api.elab.py` file and the related function calls in the notebooks.

If you wish to use the eLabFTW integration:

1. Create a `.env` file in the root directory
2. Add the following variables to the `.env` file:
	- `ELAB_API_KEY`: Your eLabFTW API key
	- `ELAB_API_URL`: Your eLabFTW instance URL

## Contact

For questions about the experiment or codebase, please contact [Your Contact Information]