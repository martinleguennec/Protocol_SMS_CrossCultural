import csv
import warnings

import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

def load_and_preprocess(file_path, fs=5000, cutoff=20, order=4):
    """
    Load and preprocess data from a CSV file.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.
    fs : int, optional
        Sampling frequency in Hz. Default is 5000.
    cutoff : float, optional
        Cutoff frequency for the low-pass filter in Hz. Default is 20.
    order : int, optional
        Order of the low-pass filter. Default is 4.

    Returns
    -------
    t : array
        Time vector.
    mov : array
        Preprocessed goniometer data.
    sound : array
        Sound signal.
    """

    # Identify the symbol used for decimal
    with open(file_path, "r") as file:
        csv_file = csv.reader(file)
        for line_idx, line in enumerate(csv_file):
            if line_idx == 1:
                decimal_symbol = str.split(line[0],";")[1][1]

    # Load the data
    data = pd.read_csv(file_path, delimiter=';', decimal=decimal_symbol, skiprows=3)
    data.columns = ['time', 'goniometer', 'time_2', 'stimulus']
    data = data.drop(columns=['time_2'])

    # Create a variable for each column
    t = data['time']
    gonio = data['goniometer']
    sound = data['stimulus']

    # Apply low-pass filter to goniometer data
    b, a = butter(order, cutoff / (fs / 2), btype='low')
    mov = filtfilt(b, a, gonio)

    return t, mov, sound

def detect_stimuli(sound, task="synch", fs=5000, plot_verif=False):
    """
    Detect stimulus onset from the sound signal.

    Parameters
    ----------
    sound : array
        Sound signal.
    task : {'synch', 'adapt', 'SMT'}, optional
        Task type. Default is 'synchro'.
    fs : int, optional
        Sampling frequency in Hz. Default is 5000.
    plot_verif : bool, optional
        Whether to plot the detected stimuli. Default is False.

    Returns
    -------
    stim_onset : array
        Indices of stimulus onset times.
    stim_times : array
        Stimulus onset times in seconds.
    plateaus : array
        Plateau start and end indices as (start, end) pairs.
    frequencies : array
        Stimulus frequencies for each plateau.
    task_onset : int
        Index of task onset.
    task_offset : int
        Index of task offset.
    """
    # Normalize the sound signal between -1 and 1
    sound = sound / np.max(np.abs(sound))

    # Find the onset of each stimuli by converting continuous values to 0 or 1
    sound_logical = np.where(np.abs(sound) > 0.1)[0]
    diff_logical = np.where(np.diff(sound_logical) > 100)[0]
    diff_logical = np.insert(diff_logical, 0, 0) + 1
    stim_onset = sound_logical[diff_logical]

    task_onset = stim_onset[0]
    task_offset = stim_onset[-1]

    if task == "synchro":
        # First detected stimulus indicates the beginning of the task and the last indicates the end
        # They are not real stimuli, but we keep them in another array for later use
        stim_onset = stim_onset[1:-1]

        # Identify plateaus based on stimulus onset
        plateaus = identify_plateaus(stim_onset)

        # The expected number of stimuli can be calculated according to the number of plateaus: the first plateau has 20
        # stimuli, and the rest have 15 stimuli each
        expected_stimuli = 20 + 15 * (len(plateaus) - 1) + 1
        # Display a warning if the number of detected stimuli does not match the expected number
        if len(stim_onset) != expected_stimuli:
            warnings.warn(f"Warning: Detected {len(stim_onset)} stimuli, but expected {expected_stimuli}.")

        # Calculate the stimulus frequencies for each plateau
        frequencies = [np.round(1/np.mean(np.diff(stim_onset[idx_start:idx_end])),1) for idx_start, idx_end in plateaus] / fs
    
    elif task == "adapt":
        plateaus = np.array([[0, 1], [2, len(stim_onset)-3], [len(stim_onset)-2, len(stim_onset)-1]])

        frequencies = np.round(1/np.mean(np.diff(stim_onset[1:len(stim_onset)-1])),1) / fs
    
    elif task == "SMT":
        plateaus = np.array([[0,1]])

        frequencies = [1]

    else:
        raise ValueError("Task must be either 'synchro' or 'adapt'.")

    # Convert to time
    stim_times = stim_onset / fs 

    if plot_verif:
        plot_stimuli_on_sound_signal(sound, stim_times, fs, task_onset, task_offset)
         

    return stim_onset, stim_times, plateaus, frequencies, task_onset, task_offset


def identify_plateaus(stim_onset):
    """
    Identify plateaus based on stimulus onset.

    Parameters
    ----------
    stim_onset : array
        Indices of stimulus onset times.

    Returns
    -------
    plateaus : array
        Plateau start and end indices as (start, end) pairs.
    """
    plateau_changes = np.where(np.abs(np.diff(np.diff(stim_onset))) > 2)[0]
    plateau_start = np.concatenate(([0], plateau_changes + 1, [len(stim_onset)]))
    plateaus = np.array([
        (plateau_start[i], plateau_start[i+1] - 1)
        for i in range(len(plateau_start) - 1)
    ])

    return plateaus

def plot_stimuli_on_sound_signal(sound, stim_onset, task_onset, task_offset, fs=5000):
    """
    Plot the sound signal with the detected stimuli.

    Parameters
    ----------
    sound : array
        Sound signal.
    stim_onset : array
        Indices of stimulus onset times.
    task_onset : int
        Index of task onset.
    task_offset : int
        Index of task offset.
    fs : int, optional
        Sampling frequency in Hz. Default is 5000.

    Returns
    -------
    None
    """
    # Create a time vector
    t = np.arange(len(sound)) / fs

    # Plot the sound signal
    plt.figure()
    plt.plot(t, sound, 'k')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Sound Signal with Detected Stimuli')

    # Plot vertical lines for each stimulus
    for stim in stim_onset:
        plt.axvline(stim, color='r')

    # Plot vertical lines for the beginning and end of the task
    plt.axvline(task_onset / fs, color='b', label='Task onset')
    plt.axvline(task_offset / fs, color='g', label='Task offset')

    plt.legend()

    plt.show()

