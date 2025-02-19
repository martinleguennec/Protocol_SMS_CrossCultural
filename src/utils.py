import numpy as np

arr = [0, 2, 4, 1, 3, 5, 7]
print(arr)


def moving_average(data, window, boundary='default'):
    """
    Compute the moving average of a 1D array with flexible window size and boundary handling.
    
    Parameters
    ----------
    data : array_like
        The input data.
    window : int or tuple
        The window size. If an integer, the window will be centered on the data point. If a tuple of two integers, the
        window will extend before the data point by the first integer and after the data point by the second integer.
    boundary : {`default`, `fill`, `omitnan`}, optional
        The boundary handling strategy. Default is `default`.
            - `default`: does not pad the data and uses smaller windows at the edges
            - `fill`: pads the data with zeros
            - `omitnan`: dynamically adjusts the window size to the number of available data points.

    Returns
    -------
    result : ndarray
        The moving average of the input data.
    """
    data = np.asarray(data, dtype=float)
    n = len(data)
    
    # Parse the window size
    if isinstance(window, int):
        before = window // 2
        after = window - before - 1
    elif isinstance(window, tuple) and len(window) == 2:
        before, after = window
    else:
        raise ValueError("Window must be an integer or a tuple of two integers.")
    
    # Initialize the result
    result = np.full(n, np.nan)  # Default to NaN for uncomputable positions

    # Boundary handling
    if boundary == 'fill':
        data = np.pad(data, (before, after), mode='constant', constant_values=0)
    elif boundary == 'default':
        pass  # No explicit padding; edges will have smaller windows
    elif boundary == 'omitnan':
        # Handle NaNs dynamically in computations
        pass
    else:
        raise ValueError("Boundary must be 'default', 'fill', or 'omitnan'.")
    
    # Compute the moving average
    for i in range(n):
        start = max(0, i - before)
        end = min(n, i + after + 1)
        if boundary == 'omitnan':
            window_data = data[start:end]
            result[i] = np.nanmean(window_data)
        else:
            result[i] = np.mean(data[start:end])

    return result

