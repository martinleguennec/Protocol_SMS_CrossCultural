"""
Stimulus Sequence Generator
===========================

This module provides functions to generate inter-onset intervals (IOIs), create sound stimuli, and combine them into a 
full stimulus sequence for experimental tasks.

The three tasks supported:
- **"pref_sync_pref"**: A reminder of the preferred frequency (3 stimuli), followed by isochronous stimuli at an 
    adjusted frequency, and a final silence period.
- **"continuation"**: Isochronous stimuli for a fixed duration followed by silence.
- **"synchro"**: A sequence of stimuli with frequency plateaus.

Functions:
----------
1. `generate_iois(frequencies, n_stimuli_per_plateau, task, ...)`
   - Generates a list of IOIs in milliseconds based on the selected task.
   
2. `generate_stimuli(ioi_list, stimulus_duration=40, sound_frequency=440, ...)`
   - Creates a list of sound stimuli matching the IOIs.
   
3. `create_sequence(ioi_list, stimuli)`
   - Combines the IOI list and stimuli into a SoundSequence.

Example Usage:
--------------
# Task 1: "pref_sync_pref" (Preferred frequency reminder, sync, then silence)
preferred_freq = 2  # Hz
sync_freq = preferred_freq * 1.3  # Adjusted by +30%
ioi_list = generate_iois(
    frequencies=[preferred_freq, sync_freq], 
    n_stimuli_per_plateau=20, 
    task="pref_sync_pref",
    silence_around_stim=[0, 30]
)
stimuli = generate_stimuli(ioi_list)
sequence = create_sequence(ioi_list, stimuli)

# Task 2: "continuation" (20s stimuli, then 40s silence)
ioi_list = generate_iois(
    frequencies=[3], 
    n_stimuli_per_plateau=20, 
    task="continuation",
    silence_around_stim=40
)
stimuli = generate_stimuli(ioi_list)
sequence = create_sequence(ioi_list, stimuli)

# Task 3: "synchro" (22 plateaus, increasing frequencies)
frequencies = [1 + i * 0.3 for i in range(22)]
ioi_list = generate_iois(
    frequencies=frequencies,
    n_stimuli_per_plateau=15,
    n_stimuli_first_plateau=20,
    task="synchro"
)
stimuli = generate_stimuli(ioi_list)
sequence = create_sequence(ioi_list, stimuli)
"""

from thebeat.core import Sequence, SoundStimulus, SoundSequence


def generate_iois(
        frequencies, 
        n_stimuli_per_plateau, 
        task,
        n_stimuli_first_plateau=None, 
        silence_around_stim=None
    ):
    """
    Generates a list of inter-onset intervals (IOI).

    Parameters
    ----------
    frequencies : list
        List of frequencies in Hz. If the task is 'pref_sync_pref', 2 frequencies must be provided. If the task is
        'continuation', 1 frequency must be provided. If the task is 'synchro', any number of frequencies can be provided.
    n_stimuli_per_plateau : int
        Number of stimuli per plateau.
    task : str
        Task to generate IOIs for. Must be 'pref_sync_pref', 'continuation', or 'synchro'.
    n_stimuli_first_plateau : int, optional
        Number of stimuli in the first plateau. Only used for 'synchro' task. If None is provided, the same number of 
        stimuli as n_stimuli_per_plateau is used.
    silence_around_stim : int or list, optional
        Silence duration in ms around each stimulus. If an int, the same duration is used before and after the stimulus.
        If a list, the first element is the silence before the stimulus and the second element is the silence after the stimulus.
        If None, no silence is added around the stimulus.

    Returns
    -------
    out : list
        List of IOIs in ms.
    """
    
    # Get silence around stimulus
    if silence_around_stim is None:
        silence_beg = silence_end = 0
    elif isinstance(silence_around_stim, int):
        silence_beg = silence_end = silence_around_stim * 1000
    elif isinstance(silence_around_stim, (list, tuple)):
        if len(silence_around_stim) == 1:
            silence_beg = silence_end = silence_around_stim[0] * 1000
        elif len(silence_around_stim) == 2:
            silence_beg, silence_end = [s * 1000 for s in silence_around_stim]
        else:
            raise ValueError("silence_around_stim must have 1 or 2 elements.")
    else:
        raise TypeError("silence_around_stim must be None, an int, or a list/tuple.")


    if task == "pref_sync_pref":
        # 2 frequencies should be provided
        if len(frequencies) != 2:
            raise ValueError("For task 'pref_sync_pref', 2 frequencies must be provided.")
        
        # 3 stimuli at the preferred frequency + silence of remainder 20s
        initial_ioi = 1000 / frequencies[0]
        initial_stim_duration = 3 * initial_ioi
        silence_after_initial_stim = max(0, (silence_beg) - initial_stim_duration)
        ioi_list = [initial_ioi * 2] + [initial_ioi] * 2 + [silence_after_initial_stim]

        # Stimuli at the modified frequency
        ioi_list.extend([1000 / frequencies[1]] * n_stimuli_per_plateau)

        # Silence at the end
        ioi_list.append(silence_end)
    
    elif task == "continuation":
        # 1 frequency should be provided
        if len(frequencies) != 1:
            raise ValueError("For task 'continuation', 1 frequency must be provided.")
        
        # Generate IOI list
        ioi_list = [silence_beg]
        ioi_list.extend([1000 / frequencies[0]] * n_stimuli_per_plateau)
        ioi_list.append(silence_end)

    elif task == "synchro":
        # If n_stimuli_first_plateau is not provided, use n_stimuli_per_plateau
        n_stimuli_first_plateau = n_stimuli_per_plateau if n_stimuli_first_plateau is None else n_stimuli_first_plateau

        # Generate IOI list
        ioi_list = [silence_beg]
        for i, freq in enumerate(frequencies):
            ioi = 1000 / freq  # Calculate IOI in ms
            n_events = n_stimuli_first_plateau if i == 0 else n_stimuli_per_plateau
            ioi_list.extend([ioi] * n_events)

        ioi_list.append(silence_end)

    else:
        raise ValueError("Invalid task. Must be 'pref_sync_pref', 'continuation', or 'synchro'.")
       

    return ioi_list


def generate_stimuli(
        ioi_list, 
        stimulus_duration=40, 
        sound_frequency=440, 
        ramp_duration=5, 
        duration_bip_start_end=500
    ):
    """
    Generates stimuli matching the IOIs, including the initial long stimulus.

    Parameters
    ----------
    ioi_list : list
        List of inter-onset intervals in ms.
    stimulus_duration : int, optional
        Duration of the stimulus in ms.
    sound_frequency : int, optional
        Frequency of the sound in Hz.
    ramp_duration : int, optional
        Duration of the on- and off-ramps in ms.
    duration_bip_start_end : int, optional
        Duration of the bip at the start and end of the sequence in ms.

    Returns
    -------
    out : list
        List of SoundStimulus objects.
    """
    stimulus = SoundStimulus.generate(
        freq=sound_frequency,
        duration_ms=stimulus_duration,
        onramp_ms=ramp_duration,
        offramp_ms=ramp_duration,
    )

    bip_start_end = SoundStimulus.generate(
        freq=sound_frequency,
        duration_ms=duration_bip_start_end,
        onramp_ms=ramp_duration,
        offramp_ms=ramp_duration,
    )

    return [bip_start_end] + (len(ioi_list)-1) * [stimulus] + [bip_start_end]


def create_sequence(ioi_list, stimuli):
    """
    Combines stimuli with the IOI sequence.

    Parameters
    ----------
    ioi_list : list
        List of inter-onset intervals in ms.
    stimuli : list
        List of SoundStimulus objects.

    Returns
    -------
    out : SoundSequence
        SoundSequence object.
    """
    full_sequence = Sequence(ioi_list)
    full_sequence.round_onsets()  # Avoid warning about rounding off onsets
    return SoundSequence(stimuli, full_sequence)
