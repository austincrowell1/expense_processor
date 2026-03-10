import datetime
import json
import logging
import numpy as np
import os
import pandas as pd

# globals
fn_run_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
run_date = datetime.datetime.now().strftime("%Y-%m-%d")
app_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(app_dir,"config/config.json")

def main(kwargs):
    #set up vars
    inq_dir = kwargs["inq_dir"]
    # output_dir = kwargs["output_dir"]
    # output_template = kwargs["output_template"]
    # output_file_name = kwargs["output_file_name"].format(month_start=kwargs["month_start"],month_end=kwargs["month_end"])
    classification_csv = kwargs["classification_csv"]
    unclassified_file_name = kwargs["unclassified_file_name"].format(month_start=kwargs["month_start"],month_end=kwargs["month_end"])
    credit_file_name = kwargs["credit_file_name"].format(month_start=kwargs["month_start"],month_end=kwargs["month_end"])

    all_files = [x for x in os.scandir(inq_dir) if x.is_file()]
    # only continue if there are files to process
    if len(all_files) <= 0:
        print("no files to process")
        return
    
    #load classifications
    classifications = pd.read_csv(classification_csv,quotechar="\"")
    # normalize classifications - put the normalized classifications in the csv so i dont have to do this every time
    classifications["classifications"] = classifications["classification"].str.lower()
    classifications["keyword"] = classifications["keyword"].str.lower()

    # set up list for output dfs
    df_list = []
    
    # iterate through known file types based on config and process specific format
    for bank_file in all_files:
        if "ally" in bank_file.name.lower():
            # read file to df
            file_df = pd.read_csv(bank_file.path)
            # normalize column names & data
            file_df.columns = [x for x.lower().strip() for x in file_df.columns]
            file_df = file_df.astype(str)
            file_df = file_df.drop("time",axis=1)
            # add additional columns
            file_df.insert(0,"bank_name","ally")
            file_df.insert(4,"classification"."")
            #repurpose type field
            file_df["type"] = ""
            # clean up the data
            file_df.loc[file_df["amount"].str.startswith("-"), "type"] = "expense"
            file_df.loc[~file_df["amount"].str.startswith("-"), "type"] = "revenue"
            file_df.["amount"] = file_df["amount"].str.replace("-","").replace(",","")
            # remove credit payments, these will come in from discover bank file
            remove_credit = ["DISCOVER E-PAYMENT","CHASE CREDIT CRD AUTOPAY"]
            file_df = file_df.loc[~file_df["description"].isin(remove_credit)]

            df_list.append(file_df)

        if "capitalone" in bank_file.name.lower():
            # read file to df
            file_df = pd.read_csv(bank_file.path)
            # normalize column names & data
            file_df.columns = [x for x.lower().strip() for x in file_df.columns]
            file_df = file_df.astype(str)
            file_df = file_df.rename(columns={"transaction date":"date"})
            # add new columns
            file_df.insert(0,"bank_name","capitalone")
            file_df.insert(3,"type","")
            file_df.insert(4,"classification","")
            file_df.insert(5,"amount","")
            # sort credit & debit columns into amount and use to update type. then drop columns
            file_df["type"] = np.where(file_df["debit"] != "", "expense", "revenue")
            file_df["amount"] = np.where(file_df["debit"] != "", file_df["debit"], file_df["credit"])
            file_df = file_df.drop(["posted date","card no.","category","debit","credit"],axis=1) #inplace=True what does this do? is it even needed?

            df_list.append(file_df)

    # combine cleaned up file data
    output_df = pd.concat(file_df)

    """
    remove discover, capital one, and chase payments listed on the credit card statements -
    these would be redundant with the credit card transactions included
    """
    credit_df_list = [] #what do i need this for again?
    # discover
    discover_names = ["DIRECTPAY FULL BALANCESEE DETAILS OF YOUR NEXT DIRECTPAY BELOW","INTERNET PAYMENT - THANK YOU"]
    discover_df = output_df.loc[output_df["description"].isin(discover_names)]
    credit_df_list.append(discover_df)
    
    # chase
    chase_names = ["AUTOMATIC PAYMENT - THANK"]
    chase_df = output_df.loc[output_df["description"].isin(chase_names)]
    credit_df_list.append(chase_df)

    # capital one
    capitalone_names = ["CAPITAL ONE AUTOPAY PYMT"]
    capitalone_df = output_df.loc[output_df["description"].isin(capitalone_names)]
    credit_df_list.append(chase_df)
    
    # remove credit payments from output
    all_names = discover_names+chase_names+capitalone_names
    output_df = output_df.loc[~output_df[description].isin(all_names)]


    # classify transactions
    output_df["description"] = output_df["description"].str.lower()
    for row in classifications.itertuples():
        mask = (
            output_df["description"].str.contains(row.keyword,regex=False)
            & output_df["classification"] == ""
        )
        output_df.loc[mask, "classification"] = row.classification


    # look through iterable version of file and match on known transactions
    # save unknown transactions to a seperate iterable so it can be output (and maybe eventually processed)
    # output final data and unclassified transactions

if __name__ == "__main__":
    # set up logging
    log_filename = os.path.join(app_dir,f"logs/expense_processor_{fn_run_datetime}.log")
    logging.basicConfig (
        filename = log_filename,
        level = logging.INFO,
        format = "%(asctime)s - %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger()

    print("---- APP START ----")
    logger.info("---- APP START ----")

    # load config
    with open(config_dir) as config_file:
        config = json.load(config_file)
    
    _kwargs = config

    main(_kwargs)