# //////////////////////////////////////////////////////
#                    PIPELINE FLOW
# //////////////////////////////////////////////////////

import pandas as pd 

import os 

from flow.pipe_base import PipelineBase
from functions.functions_I import fetch_table

import warnings
warnings.filterwarnings("ignore")

class PipelineFlow(PipelineBase):

    # Pipeline initialization
    def __init__(self) -> None:
        super().__init__()


    # --- RUN ---
    def run(self):

        s = self.config

        # Step . Show Tables
        os.makedirs(s.out_csv_path, exist_ok=True)      
        table_show = self.call_fetch_table(                   
            table_name=str(s.dbtable),
            out_path=str(f"{s.out_csv_path}{s.dbtable}.csv"),
        )

        # 




        return table_show

    
#/////////////////////////////////////
#           CALL FUNCTIONS
#/////////////////////////////////////


    # Step . Show Tables
    def call_fetch_table(self, table_name, out_path):

        s = self.config

        # Compile
        table = fetch_table(api_url=s.api_url, table=table_name, del_cols=s.del_cols)

        #Export 
        table.to_csv(out_path, index=False)

        # Success
        print(f"\n------------------- Table Loaded -------------------\n")
        return table