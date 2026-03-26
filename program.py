import argparse
import datetime
from dotenv import load_dotenv
import fnmatch
import gspread
import json
import logging
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import snowflake.connector as sc
from snowflake.connector.pandas_tools import write_pandas
import sys

from preprocessing import preprocessing
from utils import snowflake_client, gsheets_client

# globals
fn_run_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
run_date = datetime.datetime.now().strftime("%Y-%m-%d")
app_dir = os.path.dirname(os.path.abspath(__file__))


def main(kwargs):
    # set up config vars
    setup = kwargs["setup"]
    load_files = kwargs["load_files"]
    update_cat = kwargs["update_categories"]
    refresh_gsheet = kwargs["refresh_gsheet"]
    inq_dir = kwargs["inq_dir"]
    output_dir = kwargs["output_dir"]
    preproc_files = kwargs["preproc_files"]
    conn_params = kwargs["conn_params"]
    config_table = kwargs["config_table"]
    col_maps = kwargs["column_mappings"]
    cat_proc = kwargs["categories_proc"]
    uncat_proc = kwargs["uncategorized_proc"]
    uncat_fn_base = kwargs["uncategorized_file_name"]
    get_expenses_proc = kwargs["get_expenses_proc"]
    google_creds = kwargs["google_creds_file"]
    sheets_scope = kwargs["sheets_scope"]
    exp_sheet = kwargs["expense_sheet"]

    # set up snowflake_client
    sc = snowflake_client(logger, conn_params)

    if setup:
        # set up directories
        if not os.path.exists(inq_dir):
            os.makedirs(inq_dir)
            print(f"folder created: {inq_dir}")
            logger.info(f"folder created: {inq_dir}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"folder created: {output_dir}")
            logger.info(f"folder created: {output_dir}")

        # create tables, dataloads, procs
        setup_dir = kwargs["setup_dir"]
        setup_scripts = kwargs["setup_scripts"]
        setup_order = ["tables","dataloads","procedures"]

        for script_type in setup_order:
            print(f"setup: {script_type}")
            logger.info(f"setup: {script_type}")
            scripts_dir = os.path.join(setup_dir,setup_scripts[script_type])
            script_files = [x for x in os.scandir(scripts_dir) if x.is_file() and x.name.endswith(".sql")]
            
            if len(script_files) <= 0:
                print(f"    no {script_type} scripts to run")
                logger.info(f"    no {script_type} scripts to run")
            else:
                for script_file in script_files:
                    with open(script_file, 'r') as file:
                        script = file.read()
                    sc.run_script(script)
                    print(f"    {script_file} complete")
        
        print("setup complete, run the app again without --setup to begin processing expenses")
        logger.info("setup complete, run the app again without --setup to begin processing expenses")

        return
    
    if load_files:
        # get files the process
        all_files = [x for x in os.scandir(inq_dir) if x.is_file()]

        # check if there are files to process
        if len(all_files) <= 0:
            print("no files to process")
            logger.info("no files to process")
        else:
            # create archive folder
            archive_dir_path = os.path.join(inq_dir,f"archive_{fn_run_datetime}")
            if not os.path.exists(archive_dir_path):
                os.makedirs(archive_dir_path)
                print(f"archive folder created: {archive_dir_path}")
                logger.info(f"archive folder created: {archive_dir_path}")

            num_files = str(len(all_files))
            print(f"processing {num_files} files")
            logger.info(f"processing {num_files} files")

            # set up preprocessor
            pp = preprocessing(logger,archive_dir_path,preproc_files)

            # get file load config
            config_query = f"SELECT * FROM {config_table};"
            config_log = sc.run_query_get_dataframe(config_query)
            file_patterns = config_log["FILE_PATTERN"].unique()

            for bank_file in all_files:
                print(f"processing {bank_file.name}")
                logger.info(f"processing {bank_file.name}")

                for file_pattern in config_log["FILE_PATTERN"]:
                    if fnmatch.fnmatch(bank_file.name.lower(),file_pattern):
                        # get full df row for matched config
                        match_config = config_log[config_log["FILE_PATTERN"] == file_pattern].iloc[0]

                        # set up config vars
                        feed_name = match_config["FEED_NAME"]
                        raw_table = match_config["RAW_TABLE"]
                        proc = match_config["STORED_PROC"]
                        print(f"    loaded {feed_name} config")
                        logger.info(f"    loaded {feed_name} config")

                        # run preprocessing
                        print(f"    preprocessing: {bank_file.name}")
                        logger.info(f"    preprocessing: {bank_file.name}")
                        file_df = pp.file_preprocessing(bank_file,col_maps[feed_name])

                        # load file to snowflake
                        success, num_chunks, num_rows, _ = sc.load_data_snowflake(file_df, raw_table)
                        print(f"    loaded {str(num_rows)} records to {raw_table}")
                        logger.info(f"    loaded {str(num_rows)} records to {raw_table}")

                        # run proc to cleanse data and load to final table
                        proc_results = sc.run_query_get_results(f"CALL {proc}('{feed_name}');")
                        print(f"    {proc_results}")
                        logger.info(f"    {proc_results}")

                        # archive file
                        archive_file_path = os.path.join(archive_dir_path,bank_file.name)
                        os.rename(bank_file.path,archive_file_path)
                        print(f"    archived to {archive_dir_path}")
                        logger.info(f"    archived to {archive_dir_path}")

    # categorize transactions
    if update_cat:
        cat_results = sc.run_query_get_results(f"CALL {cat_proc}();")
        print(f"{cat_proc} results: {cat_results}")
        logger.info(f"{cat_proc} results: {cat_results}")

        # get uncategorized transactions and output to csv
        uncat_results = sc.run_query_get_dataframe(f"CALL {uncat_proc}();")
        uncat_file_name = os.path.join(output_dir,f"{uncat_fn_base}_{fn_run_datetime}.csv")
        uncat_results.to_csv(uncat_file_name, index=False)
        print(f"uncategorized transactions output to: {uncat_file_name}")
        logger.info(f"uncategorized transactions output to: {uncat_file_name}")

    if refresh_gsheet:
        # get final expenses
        output_df = sc.run_query_get_dataframe(f"CALL {get_expenses_proc}();")

        # refresh google sheets data source
        # tableau public can't use the API so I'm using a google sheets data source as the bridge
        gc = gsheets_client(google_creds, sheets_scope)
        gc.refresh_data(output_df, exp_sheet)
        print(f"google sheet {exp_sheet} refreshed")
        logger.info(f"google sheet {exp_sheet} refreshed")

    sc.close_conn()


def handle_errors(e_type, e_value, e_traceback):
    if issubclass(e_type, KeyboardInterrupt):
        sys.__excepthook__(e_type, e_value, e_traceback)
        logger.info("app manually killed")

    logging.info("ERROR: ",exc_info=(e_type, e_value, e_traceback))


if __name__ == "__main__":
    # parse run mode from cmd line args
    parser = argparse.ArgumentParser(
        prog="expense_processor",
        description="loads credit and bank data to calculate expenses"
    )

    parser.add_argument(
        "--mode",
        choices=["test","prod"],
        default="test",
        help="pick a runtime environment (default: test)"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="setup directories and snowflake"
    )

    args = parser.parse_args()

    # logging setup
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"folder created: {log_dir}")
    
    log_filename = os.path.join(log_dir,f"{args.mode}_expense_processor_{fn_run_datetime}.log")
    logging.basicConfig (
        filename = log_filename,
        level = logging.INFO,
        format = "%(asctime)s - %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger()

    # set up error handling
    sys.excepthook = handle_errors

    print("---- APP START ----")
    logger.info("---- APP START ----")
    print(f"running in {args.mode} mode")
    logger.info(f"running in {args.mode} mode")

    # load config
    config_dir = f"config/{args.mode}_config.json"
    with open(config_dir) as config_file:
        config = json.load(config_file)
    
    # pick test or prod .env file and load
    env_path = f".env.{args.mode}"
    load_dotenv(dotenv_path=env_path)
    
    # configure snowflake connection
    conn_params = {
        "user":os.getenv("SNOWFLAKE_USER"),
        "account":os.getenv("SNOWFLAKE_ACCOUNT"),
        "private_key_file":os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"),
        "private_key_file_pwd":os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"),
        "warehouse":os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database":os.getenv("SNOWFLAKE_DATABASE"),
        "schema":os.getenv("SNOWFLAKE_SCHEMA"),
        "role":os.getenv("SNOWFLAKE_ROLE")
    }
    # add snowflake connection to config
    config["conn_params"] = conn_params

    # add setup check
    config["setup"] = args.setup

    _kwargs = config

    main(_kwargs)

    print("---- APP END ----")
    logger.info("---- APP END ----")