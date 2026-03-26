import fnmatch
import os
from pathlib import Path
import pandas as pd
from types import SimpleNamespace

class preprocessing:
#deal with junk info at top of bofa file
    def __init__(self,logger,archive_dir,preproc_files):
        # setting the class vars is a little clunky out of scalability and wanting to keep bank names annonymous
        self.logger = logger
        self.archive_dir = archive_dir
        self.preproc_file_list = SimpleNamespace(**preproc_files)

    def file_preprocessing(self, bank_file,col_map):
        # if bank_file.name in self.preproc_file_list.bank_1_fn:
        if fnmatch.fnmatch(bank_file.name.lower(),self.preproc_file_list.bank_1_fn):
            with open(bank_file.path, "r") as b1_input_file:
                lines = b1_input_file.readlines()
                # deleting rows in reverse order to maintain index
                del lines[7]
                del lines[0:6]
            
            path_bf = Path(bank_file.path)
            archive_file_name = f"{path_bf.stem}_raw{path_bf.suffix}"
            archive_file_path = Path(self.archive_dir) / archive_file_name
            path_bf.rename(archive_file_path)
            print(f"      archived: {bank_file.name} to {archive_file_path}")
            self.logger.info(f"      archived: {bank_file.name} to {archive_file_path}")
            with open(bank_file.path, "w") as b1_output_file:
                b1_output_file.writelines(lines)

        file_df = pd.read_csv(bank_file.path)
        
        # cleanse field names for mapping
        file_df.columns = file_df.columns.str.lower().str.strip()
        
        # rename the file_df fields to match the snowflake table fields
        file_df.rename(
            columns=col_map,
            inplace=True
        )
        
        # cleanse symbols from description before loading to snowflake
        file_df["description"] = file_df["description"].str.replace(r"[^a-zA-Z0-9 ]", "", regex=True).str.strip()
        
        return file_df