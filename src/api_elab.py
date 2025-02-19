import time
import json
import numpy as np
import elabapi_python as elabapi
from elabapi_python.rest import ApiException
from dotenv import load_dotenv
import os

load_dotenv()

def configure_api():
    """
    Configure the API client with the host URL and the API key.

    Returns
    -------
    api_client : elabapi.ApiClient
        The configured API client.

    Note
    ----
    The API key and the host URL are stored in the .env file. To get an API key, please refer to the eLabFTW 
    documentation.
    """
    # Get the host URL and the API key from the .env file
    API_HOST_URL = os.getenv('ELAB_API_URL')
    API_KEY = os.getenv('ELAB_API_KEY')

    # Configure the api client
    configuration = elabapi.Configuration()
    configuration.api_key['api_key'] = API_KEY
    configuration.api_key_prefix['api_key'] = 'Authorization'
    configuration.host = API_HOST_URL
    configuration.debug = False
    configuration.verify_ssl = False

    # create an instance of the API class
    api_client = elabapi.ApiClient(configuration)
    # fix issue with Authorization header not being properly set by the generated lib
    api_client.set_default_header(header_name='Authorization', header_value=API_KEY)

    return api_client


def get_experiment_id(participant):
    """
    Get the experiment id for the participant. If the experiment does not exist, create it.

    Parameters
    ----------
    participant : str
        The participant's ID.
    
    Returns
    -------
    exp_id : int
        The experiment ID.

    Notes
    -----
    The function uses the eLabFTW API to interact with the platform. Each experiment is named with the following format:
    "Martin Le Guennec - CrossCultural_Synchro_Adaptation - {participant}". The function searches for an experiment with
    the participant's ID and returns the ID of the experiment. If the experiment is not found, it creates a new one.
    """
    # Read all experiments
    api_client = configure_api()
    exp_api = elabapi.ExperimentsApi(api_client)
    exps = exp_api.read_experiments()

    # Get the experiment id for the participant
    exps_titles_id = [[exp.title, exp.id] for exp in exps]
    exp_id = None
    for exp in exps_titles_id:
        if exp[0].endswith(participant):
            exp_id = exp[1]
            break

    # If the experiment is not found, create it
    if exp_id is None:
        exp_api.post_experiment(body={"template": 7})
        exp_id = exp_api.read_experiments()[0].id
        exp_api.patch_experiment(exp_id, body={"title": f'Martin Le Guennec - CrossCultural_Synchro_Adaptation - {participant}'})
        print("ELAB INFO: Experiment created")

    return exp_id


def set_date_experiment(participant):
    """
    Set the current date in the metadata of the experiment.

    Parameters
    ----------
    participant : str
        The participant's ID.
    
    Notes
    -----
    The function uses the eLabFTW API to interact with the platform. The function gets the experiment ID for the
    participant and updates the metadata of the experiment with the current date in the "Date of experiment" field.
    """
    # Read all experiments
    api_client = configure_api()
    exp_api = elabapi.ExperimentsApi(api_client)
    exp_id = get_experiment_id(participant)

    # Get the current date in yyyy-mm-dd format
    current_date = time.strftime("%Y-%m-%d")

    # Replace the date in the metadata
    the_exp = exp_api.get_experiment(exp_id)
    extra_fields = json.loads(the_exp.metadata)
    extra_fields["extra_fields"]['Date of experiment']['value'] = current_date

    # Update the experiment's metadata
    exp_api.patch_experiment(exp_id, body={"metadata": json.dumps(extra_fields)})

    print("ELAB INFO: Date of experiment updated")


def change_text(participant, text):
    """
    Change the text of the experiment.

    Parameters
    ----------
    participant : str
        The participant's ID.
    text : str
        The new text to set in the experiment.
    
    Notes
    -----
    The function uses the eLabFTW API to interact with the platform. The function gets the experiment ID for the
    participant and updates the text of the experiment with the new text.
    """
    # Read all experiments
    api_client = configure_api()
    exp_api = elabapi.ExperimentsApi(api_client)
    exp_id = get_experiment_id(participant)

    exp_api.patch_experiment(exp_id, body={"body": text})
    print("ELAB INFO: Text updated")


def text_randomization(order_1, order_2):
    """
    Create the html code for the table for the randomization order.

    Parameters
    ----------
    order_1 : list
        The first order of the randomization.
    order_2 : list
        The second order of the randomization.
        
    Returns
    -------
    text : str
        The html code for the table.

    Notes
    -----
    The function creates an html table with the randomization order. The table has two rows: one for the first order
    and one for the second order. Each row has a cell for each condition. The background color of the cell is green for
    the "Fast" condition and red for the "Slow" condition
    """
    text = (
        '<h1>Randomization order</h1>\n'
        '<table ' 
        'style="border-collapse:collapse;width:60%;height:67.1952px;'
        'border:1px solid rgb(0,0,0);" border="1">\n' 
        '\n'
        '<tr style="height:22.3984px;">\n'
        '<td style="height:22.3984px;width:52%;">\xa0</td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>1</strong></td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>2</strong></td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>3</strong></td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>4</strong></td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>5</strong></td>\n'
        '<td style="height:22.3984px;text-align:center;width:8%;"><strong>6</strong></td>\n'
        '</tr>\n'
        '<tr style="height:22.3984px;">\n'
        '<td style="height:22.3984px;text-align:center;width:52%;"><strong>Preferred - synchronization - preferred</strong></td>\n'
    )

    for condition in ["Slow" if x == "S" else "Fast" for x in order_1]:
        if condition == 'Slow':
            text += f'<td style="height:22.3984px;text-align:center;width:8%;background-color:rgb(251,184,184);">{condition}</td>\n'
        else:
            text += f'<td style="height:22.3984px;text-align:center;width:8%;background-color:rgb(191,237,210);">{condition}</td>\n'
    
    text += (
        '</tr>\n'
        '<tr style="height:22.3984px;">\n'
        '<td style="height:22.3984px;text-align:center;width:52%;"><strong>Preferred - synchronization - continuation</strong></td>\n'
    )

    for condition in ["Slow" if x == "S" else "Fast" for x in order_2]:
        if condition == 'Slow':
            text += f'<td style="height:22.3984px;text-align:center;width:8%;background-color:rgb(251,184,184);">{condition}</td>\n'
        else:
            text += f'<td style="height:22.3984px;text-align:center;width:8%;background-color:rgb(191,237,210);">{condition}</td>\n'

    text += '</tr>\n</table>\n'
    
    return text


def text_preferred(participant, IOI_mean, IOI_sd, CV_mean):
    """
    Create the html code for the table for the preferred frequency.

    Parameters
    ----------
    participant : str
        The participant's ID.
    IOI_mean : list
        The mean inter-onset intervals for each trial.
    IOI_sd : list
        The standard deviation of the inter-onset intervals for each trial.

    Returns
    -------
    text : str
        The html code for the table.

    Notes
    -----
    The function creates an html table with the preferred frequency results. The table has three rows: one for the mean
    and standard deviation of the inter-onset intervals for each trial, one for the variation coefficient between trials,
    and one for the average frequency. The table also includes the conditions frequency (slow and fast) based on the
    average frequency. 
    It also checks whether a text is already existing for the experiment and appends the table at the beginning of the
    existing text.
    """
    # Read all experiments
    api_client = configure_api()
    exp_api = elabapi.ExperimentsApi(api_client)
    exp_id = get_experiment_id(participant)

    if exp_api.get_experiment(exp_id).body.startswith('<h1>SMT</h1>'):
        text = exp_api.get_experiment(exp_id).body

    else:
        # The first time this function is used must be the day of the experiment
        set_date_experiment(participant)

        text = (
            '<h1>SMT</h1>\n'
            '<table style="border-collapse:collapse;width:70%;height:89.5936px;" border="1">\n'
            '\n'
            '<tr style="height:22.3984px;">\n'
            '<td style="height:22.3984px;text-align:center;width:40%;">\xa0</td>\n'
            '<td style="height:22.3984px;text-align:center;width:12%;"><strong>Trial 1</strong></td>\n'
            '<td style="height:22.3984px;text-align:center;width:12%"><strong>Trial 2</strong></td>\n'
            '<td style="height:22.3984px;text-align:center;width:12%"><strong>Trial 3</strong></td>\n'
            '<td style="height:22.3984px;text-align:center;width:12%"><strong>Trial 4</strong></td>\n'
            '<td style="height:22.3984px;text-align:center;width:12%"><strong>Trial 5</strong></td>\n'
            '</tr>\n'
            '<tr style="height:22.3984px;">\n'
            '<td style="height:22.3984px;text-align:center;width:40%;"><strong>Mean ± SD (Hz)</strong></td>\n'
            f'<td style="height:22.3984px;text-align:center;width:12%">{round(IOI_mean[0], 2)} (± {round(IOI_sd[0], 2)})</td>\n'
            f'<td style="height:22.3984px;text-align:center;width:12%">{round(IOI_mean[1], 2)} (± {round(IOI_sd[1], 2)})</td>\n'
            f'<td style="height:22.3984px;text-align:center;width:12%">{round(IOI_mean[2], 2)} (± {round(IOI_sd[2], 2)})</td>\n'
            f'<td style="height:22.3984px;text-align:center;width:12%">{round(IOI_mean[3], 2)} (± {round(IOI_sd[3], 2)})</td>\n'
            f'<td style="height:22.3984px;text-align:center;width:12%">{round(IOI_mean[4], 2)} (± {round(IOI_sd[4], 2)})</td>\n'
            '</tr>\n'
            '<tr style="height:22.3984px;">\n'
            '<td style="height:22.3984px;text-align:center;width:40%;"><strong>Variation coefficient between trials</strong></td>\n'
            f'<td style="height:22.3984px;text-align:center;width:60%;" colspan="5">{round(CV_mean,2)} %</td>\n'
            '</tr>\n'
            '<tr style="height:22.3984px;">\n'
            '<td style="height:22.3984px;text-align:center;width:40%;"><strong>Average frequency</strong></td>\n'
            f'<td style="height:22.3984px;text-align:center;width:60%;" colspan="5">{round(np.mean(IOI_mean),2)} Hz</td>\n'
            '</tr>\n'
            '\n'
            '</table>\n'
            '\n'
            '<h2>Conditions frequency</h2>\n'
            '<ul>\n'
            f'<li><strong>Slow:</strong> {round(0.8*np.mean(IOI_mean),2)}  Hz</li>\n'
            f'<li><strong>Fast:</strong> {round(1.2*np.mean(IOI_mean),2)} Hz</li>\n'
            '</ul>\n'
            '<p>\xa0</p>\n'
            '<hr>\n'
        )

        text += exp_api.get_experiment(exp_id).body

    return text