# //////////////////////////////////////////////////////
#                    PIPELINE BASE 
# //////////////////////////////////////////////////////

import logging 
import os
import yaml 

from dataclasses import dataclass
from abc import ABC, abstractmethod

# --- CONFIGURATION ---

@dataclass
class Config:

    # Variables
    dbtable: str
    out_csv_path: str
    out_fig_path: str
    api_url: str
    del_cols: list

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
# --- PARSE CONFIG ---
def parse_config():
    pipeline_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(pipeline_dir), "config")

    base_config = os.path.join(config_path, "base.yaml")
    with open(base_config, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    
    input_config = os.path.join(config_path, "case.yaml")
    if os.path.exists(input_config):
        with open(input_config, "r") as file:
            data_input = yaml.load(file, Loader=yaml.FullLoader)
        data.update(data_input)

    config = Config.from_dict(data)
    return config

# --- PIPELINE BASE ---
class PipelineBase(ABC):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = parse_config()

    @abstractmethod
    def run(self):
        pass

