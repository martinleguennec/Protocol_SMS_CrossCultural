from numpy import random
import numpy as np

def randomize_conditions(participant_number):
    """
    Randomize the order of the conditions for the two tasks.

    This function uses a fixed seed to randomize the order of the conditions for the two tasks, depending only on the
    participant number. This ensures that: 
        - The same participant will always receive the same order of conditions.
        - Each participant will receive a different order of conditions.
        - Each possible order of conditions will be assigned to a participant, before any order is repeated.

    Parameters
    ----------
    participant_number : int
        The number of participants.

    Returns
    -------
    order_1 : array_like
        The randomized order of the conditions for the first task.
    order_2 : array_like
        The randomized order of the conditions for the second task.
    """

    random.seed(0)

    arr = np.array(["F", "F", "F", "S", "S", "S"])

    # Randomize order for the first task
    for i in range(participant_number):
        arr_shuff = random.permutation(6)
        order_1 = arr[arr_shuff]

    # Randomize order for the second task
    for i in range(participant_number):
        arr_shuff_2 = random.permutation(6)
        order_2 = arr[arr_shuff_2]

    return order_1, order_2