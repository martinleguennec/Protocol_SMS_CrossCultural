# Protocol_SMS_CrossCultural_2025

This repository contains the experimental code used to investigate sensorimotor synchronization mechanisms of frequency adaptation, comparing French and Indian participants.

## Project Structure

The project is organized into the following directories:

```bash
/data
    └── participant_id/
          └── participantID_SMT__trialNb.csv
/src
    └── [Python source files with experimental functions]
/notebooks
    ├── randomization.ipynb             # Randomizes experimental conditions
    ├── calculate_preferred_freq.ipynb  # Processes CSV files to compute preferred frequencies
    └── generate_stimuli.ipynb          # Generates stimuli based on experimental parameters
requirements.txt                        # Lists required Python libraries
```

### data/
Contains participant csv files of the spontaneous motor tempo measurements. Each participant should have their own subdirectory.

Expected file naming convention:
- `participantID_Pref__trialNb.csv`

`trialNb` goes from 1 to 5, since each participant should perform 5 SMT trials.

> Note: The data directory is initially empty. Create individual participant folders as you conduct the experiment.

### src/
Contains Python source files with functions used throughout the experiment. These functions support various experimental tasks and data collection processes.

### notebooks/
Contains three Jupyter notebooks that are essential for running the experiment:

- `randomization.ipynb`: Handles randomization procedures for the experiment
- `calculate_preferred_freq.ipynb`: Processes and calculates preferred frequencies
- `generate_stimuli.ipynb`: Creates stimuli based on experimental parameters

Note: These notebooks utilize functions from the src/ directory.

## Getting Started

### Python configuration

1. **Create a Virtual Environment**
   It is recommanded to create a virtual environment to manage libraries. Run the following command based on your operating system:

   ```python
   # macOS/Linux
   python3 -m venv .venv

   # Windows
   python -m venv .venv
   ```

2. **Activate the Virtual Environment**

   ```python
   # macOS/Linux
   source .venv/bin/activate

   # Window
   .venv/Scripts/activate
   ```

3. **Install Required Libraries**
   
   With the virtual environment activated, install all dependencies using the `requirements.txt` file:

   ```python
   pip install -r requirements.txt
   ```


### Running the experiment

1. **Data Setup**
   For each new participant, create a folder inside the `data/` directory and save their csv files using the naming convention `participantID_SMT__trialNb.csv`.
2. **Execute the Notebooks in Order**


## Contact

For questions about the experiment or codebase, please contact martin.le-guennec@umontpellier.fr
