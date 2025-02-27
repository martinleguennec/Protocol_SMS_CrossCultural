import numpy as np
from numpy import random

def has_three_in_a_row(order):
    """
    Check if the given order contains three identical consecutive elements.
    """
    for i in range(len(order) - 2):
        if order[i] == order[i + 1] == order[i + 2]:
            return True
    return False

def randomize_conditions(participant_number):
    """
    Randomize the order of the conditions for two tasks and a third set of conditions,
    ensuring that no three consecutive elements are identical.
    
    The function sets the random seed based on the participant number so that:
        - The same participant always receives the same order.
        - Different participants receive different orders.
    
    Parameters
    ----------
    participant_number : int
        The participant's number used as a seed for deterministic randomization.
    
    Returns
    -------
    order_1 : array_like
        The randomized order for the first task.
    order_2 : array_like
        The randomized order for the second task.
    order_3 : array_like
        The randomized order for the third condition set.
    """
    # Set the random seed using the participant number for reproducibility
    random.seed(participant_number)
    
    # Conditions for the first two tasks (three "F" and three "S")
    arr = np.array(["F", "F", "F", "S", "S", "S"])
    
    # Generate order_1 with reshuffling if three consecutive conditions are found
    order_1 = arr[random.permutation(6)]
    while has_three_in_a_row(order_1):
        order_1 = arr[random.permutation(6)]
    
    # Generate order_2 similarly
    order_2 = arr[random.permutation(6)]
    while has_three_in_a_row(order_2):
        order_2 = arr[random.permutation(6)]
    
    # Conditions for the third task (three "I" and three "D")
    arr_2 = np.array(["I"] * 4 + ["D"] * 4)
    
    # Generate order_3 with reshuffling if needed
    order_3 = arr_2[random.permutation(8)]
    while has_three_in_a_row(order_3):
        order_3 = arr_2[random.permutation(8)]
    
    return order_1, order_2, order_3
