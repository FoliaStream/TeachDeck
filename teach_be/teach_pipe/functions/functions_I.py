# //////////////////////////////////////////////////////
#                  FUNCTIONS I LEVEL
# //////////////////////////////////////////////////////

import os 
import shutil
import requests

import pandas as pd 



#----------------------
# STEP . Fetch table
#----------------------

def fetch_table(api_url: str, table, del_cols, params: dict | None = None) -> pd.DataFrame:

    url = f"{api_url.rstrip('/')}/tables/{table}"          
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Cannot reach the API at {url}. Is the API running?")
    except requests.exceptions.HTTPError as err:
        raise RuntimeError(f"The API answered with an error for {url}: {err}")

    table = pd.DataFrame(response.json())
    table = table.drop(columns=del_cols, errors="ignore")
    return table



