"""
IDENTIFY PEAK FLEXION IN SIMPLEMENT OSCILLATING MOVEMENTS
=========================================================
This script detects and validates peaks in movement data, specifically to identify meaningful flexion-extension cycles
in a sensorimotor synchronization task. It handles irregular movements at low frequencies and ensures robustness against
movements with multiple local maxima.

Date of Creation: 2024-11-21
Author: Martin Le Guennec
Email: martin.le-guennec@umontpellier.fr

Notes
-----
This method was designed for analyzing finger movements, measured by a goniometer, in a synchronization task where 
participants moved their finger along with a metronome. It assumes goniometer data has been filtered to correctly detect
movement peaks.

The different thresholds used in this function were determined empirically based on the characteristics of the movement
data. They may need to be adjusted for different datasets.
"""

import numpy as np
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
import warnings

from src.utils import moving_average

def extract_and_normalize_movement(movement, start, end, stim_freq, fs=5000):
    """
    Extract and normalize movement data between a start and end index.

    Parameters
    ----------
    movement : array
        The raw movement signal.
    start : int
        Start index for extraction.
    end : int
        End index for extraction.
    stim_freq : float
        Stimulus frequency in Hz.
    fs : int, optional
        Sampling frequency in Hz. Default is 5000.

    Returns
    -------
    out : array
        Normalized movement signal, scaled to the range [0, 100].
    """

    movement = movement[start:end]

    # Eliminate movement fluctuation by substracting moving average over 3 movements
    window_length = int(3 / stim_freq * fs)
    movement_centered = movement - moving_average(movement, window_length)

    # Normalize the movement between 0 and 100
    movement_normalized = movement_centered - np.min(movement_centered)
    movement_normalized = movement_normalized / np.max(movement_normalized) *100

    return movement_normalized


def plot_peak_on_movement(movement, detected_peaks, fs=5000):
    plt.figure()
    t = np.arange(len(movement)) / fs
    plt.plot(t, movement, 'k')
    plt.plot(t[detected_peaks], movement[detected_peaks], 'ro')
    plt.xlabel('Time (s)')
    plt.ylabel('Normalized Movement')
    plt.title('Detected Peaks on Movement Signal')
    plt.show()


def identify_peak_flexion(
    movement, 
    stim_onset, 
    plateaus, 
    fs=5000, 
    peak_threshold=50, 
    min_velocity_sum=60, 
    frequency_threshold=7.3, 
    debugging=False, 
    plot_verif=False
):
    """
    Identify peak flexion moments in movement data.

    This function identifies valid flexion-extension peaks in a movement signal. Peaks are initially detected based on 
    their height in the normalized signal. Each peak is validated by calculating the total movement (sum of absolute 
    velocity changes) between it and the previous peak. Peaks are only retained if the total movement exceeds a certain
    threshold (`min_velocity_sum`), ensuring the peak represents a full flexion-extension cycle. This approach is
    necessary at low frequencies where some participants kept their finger in flexion for a long time, leading to 
    multiple peaks within a single movement.

    Parameters
    ----------
    movement : array
        The movement signal (e.g., filtered goniometer data).
    stim_onset : array
        Indices of stimulus onset times.
    plateaus : array
        Plateau start and end indices as (start, end) pairs.
    fs : int, optional
        Sampling frequency in Hz. Default is 5000.
    peak_threshold : float, optional
        Minimum height for peaks in normalized movement signal. Default is 50.
    min_velocity_sum : float, optional
        Minimum sum of absolute velocity between peaks to consider valid. Default is 60.
    frequency_threshold : float, optional
        Frequency threshold for direct peak detection. Default is 7.3 Hz.
    debugging : bool, optional
        Whether to print debugging information. Default is False.
    plot_verif : bool, optional
        Whether to plot the detected peaks on the movement signal. Default is False.

    Returns
    -------
    out : array
        Detected peak indices in the movement signal.
    """

    detected_peaks = []
    last_peak_idx = 0

    if debugging:
        print("BEGIN PEAK DETECTION...")

    for plateau_idx in range(len(plateaus)):

        # Calculate stimulus frequency for the current plateau.
        # If there is no stimulus (preferred frequency measurement), set the frequency to 2 Hz by default.
        # This approximates a typical movement frequency for this task. Having a frequency close to that of the movement
        # is necessary for correct normalization of the movement.
        if plateaus[plateau_idx, 1] - plateaus[plateau_idx, 0] == 1:
            stim_freq = 2
        else: 
            stim_freq = fs / np.mean(np.diff(stim_onset[plateaus[plateau_idx, 0]:plateaus[plateau_idx, 1]]))
        
        if debugging:
            print(f"    Plateau {plateau_idx + 1} - Stimulus frequency: {stim_freq:.2f} Hz...")

        plateau_end = stim_onset[plateaus[plateau_idx, 1]] + 1
        if plateau_idx == 0:
            plateau_start = stim_onset[0]
        else:
            plateau_start = stim_onset[plateaus[plateau_idx - 1, 1]] -1

        plateau_mov = extract_and_normalize_movement(movement, plateau_start, plateau_end, stim_freq)

        # At low frequencies, movements can have shapes that prevent simple peak detection.
        # In such cases, we need to validate the peaks by checking the total movement between them.
        # This issue is more likely to occur when the frequency is below the specified threshold.
        # For frequencies above this threshold, movements are more regular, allowing direct peak detection.
        if stim_freq < frequency_threshold:
            initial_peaks = find_peaks(plateau_mov, height=peak_threshold)[0]

            valid_peaks = []

            # For the first plateau, we consider that the first peak flexion is the first detected peak.
            if plateau_idx == 0:
                valid_peaks.append(initial_peaks[0])
                first_peak_idx = 1

            # For the other plateaus, calculate the total amount of movement between the last detected peak for the
            # previous plateau and the first detected peak for the current plateau.
            # If it exceeds a certain threshold, first peak detected is considered first peak flexion.
            else:
                mov_between_peaks = movement[last_peak_idx:plateau_end]
                mov_between_peaks = mov_between_peaks - np.min(mov_between_peaks)
                mov_between_peaks = mov_between_peaks / np.max(mov_between_peaks) * 100

                first_peak_idx = 0

                temp_start = 0
                temp_end = initial_peaks[first_peak_idx] + plateau_start - last_peak_idx

                while np.sum(np.abs(np.diff(mov_between_peaks[temp_start:temp_end]))) < min_velocity_sum:
                    first_peak_idx += 1
                    temp_end = initial_peaks[first_peak_idx] + plateau_start - last_peak_idx

                    if peak_idx >= len(initial_peaks):
                        break

                valid_peaks.append(initial_peaks[first_peak_idx])

            # Validate the other peaks by checking the total movement between them.
            for peak_idx in range(1, len(initial_peaks)):
                previous_peak = initial_peaks[peak_idx - 1]
                current_peak = initial_peaks[peak_idx]

                velocity = np.diff(plateau_mov[previous_peak:current_peak])
                velocity_sum = np.sum(np.abs(velocity))

                if velocity_sum > min_velocity_sum:
                    valid_peaks.append(current_peak)
            
            # Update the last peak index for the next plateau
            last_peak_idx = valid_peaks[-1] + plateau_start
            detected_peaks.extend(valid_peaks + plateau_start)
        
        else:  # Frequency above fixed threshold
            min_distance = int(fs / stim_freq / 2)
            peaks_in_plateau = find_peaks(plateau_mov, distance=min_distance)[0]
            detected_peaks.extend(peaks_in_plateau + plateau_start)
        
        # Debugging information
        if len(detected_peaks) == 0:
            warnings.warn(f"No peaks detected in plateau {plateau_idx + 1}.")
        if debugging:
            print("        Done!")
        
    # Remove duplicates
    detected_peaks = np.unique(detected_peaks)

    if plot_verif:
        plot_peak_on_movement(movement, detected_peaks, fs)
        
    return detected_peaks