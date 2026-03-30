# Expense Processor
Track your finances without the hassle!

## About The Project
Expense Processor is a Python and SQL based ETL and data vizualization app for tracking personal finanaces. It's designed to:
- extract and cleanse bank and credit card transaction data
- load transaction data to snowflake where it is standardized
- categorize each transaction into pre-defined categories (you can define your own! - more on that later)
- pull final transaction data from snowflake into a Google Sheet
- visualize finances via Tableau Public dashboard using Google Sheet as data source

Each of these functionalities can be run modularly. I.E. only load data to snowflake or only categorize transactions and push to Google Sheets.

Expense Processor supports multiple environments. Currently it is configured to work with a Test and Prod environment but that could be easily reconfigured or expanded to include any number or environments.

A quick note on Google Sheets - Because Tableau Public doesn't have access to the API, Google Sheets automates the Tableau data refresh by acting as a bridge between the Snowflake DB and Tableau Public. If you have access to enterprise-level Tableau, Google Sheets could be eliminated entirely and replaced with a Tableau API integration.


## Getting Started
### Prerquisites
#### Snowflake
- Create a Snowflake account and a DB user account, warehouse, and database for the app to use
- Generate a PKCS8 key pair
    - Easiest to do in Git Bash
    - Snowflake only accepts PKCS8 key pairs
    - This app is only set up to authenticate Snowflake via keypair due to the sensitivity of financial data
    ```sh
    -- gens pkcs1 key
    openssl genrsa -aes256 -out snowflake_key.p8

    -- converts pkcs1 key to pkcs8 required by Snowflake
    openssl pkcs8 -topk8 -inform PEM -outform PEM -in snowflake_key.p8 -out         snowflake_key_pkcs8.p8

    -- generates public key
    openssl rsa -in snowflake_key.p8 -pubout -out snowflake_key.pub
    ```
- Associate public key with account in Snowflake
    ```sql
        ALTER USER <YOUR_USER>
        SET RSA_PUBLIC_KEY='ThisIsAPublicKey';

        -- Verify
        DESC USER <YOUR_USER>;
    ```
#### Google Sheets
To interface with the Google Sheets API, you have to do some set up in the [Google Cloud Console](https://console.cloud.google.com/):
- create a new project and enable the Google Sheets API and the Google Drive API
- create a service account:
    - Credentials > Create Credentials > Service Account
- create an auth key for the account:
    - [service account] > Keys > Add Key > Create New Key (JSON).
- create a Google Sheet to store transaction data and **share the sheet with the service account's email**

#### Transaction Data
Currently, Expense Processor only loads transaction data through .csv files which are available to download from banks/credit institutions.

#### Pipenv
All dependencies can be loaded via pipenv environment
```sh
pip install pipenv
```
### Installation
1. clone the repo
    ```sh
    git clone https://github.com/austincrowell1/expense_processor.git
    ```
2. install the pipenv
    ```sh
    pipenv install
    ```
3. Configure for your banks/credit institutions. Review your csv data and do the following:
    - keep in mind when reviewing .csv data and updating the procs that this project assumes credit transaction have negative values and debit transactions have positive.
    - update preprocessing.py with any .csv specific cleanses and add their file naming convention to "preproc_files" in config.json. 
        - This deals with any junk/non-.csv data that shows up in the .csv files for an oddly large number of banks...
    - update the table creation script in snowflake_scripts_test/tables to have a table for each of your institutions that matches the .csv schema (minus the field names - that's next)
    - update "column_mappings" in config.json to match the .csv field name to the table field names
    - update procs in snowflake_scripts_test/procedures to account for any institution level transformations needed to standardize the data when loading to the final table
        - it's likely that one of the sample procs already has all the transformations you need as they were based on data from many common banks/credit institutions
    - update data load to config_log in snowflake_scripts_test/dataloads to match the .csv file, table, and proc names for your institutions
4. update config.json: add path to your Google creds file to "google_creds_file", the name of your google sheet to "expense_sheet", and update any paths to match your paths

### Configuring Environments
Out of the box the app works with 2 environments, test & prod. This can be changed or expanded to include any number of environments.


For each environment you will need:
- a separate config updated with the correct paths for that environment
    - naming convention is &lt;env_name&gt;_config.json - I.E. test_config.json
- a separate .env file
    - naming convention is .env.&lt;env_name&gt; - I.E. .env.test
- to add an environment name other than test and prod to the argument choices in program.py:
    ```python
    parser.add_argument(
        "--mode",
        choices=["test","prod","your_new_env"],
        default="test",
        help="pick a runtime environment (default: test)"
    )
    ```

### Command Line Arguments
Expense Processor takes 2 different command line arguments:
- --mode env_name
    - determines the runtime environment of the app
    - out of the box the app has 2 modes - test and prod
    - defaults to test if argument isn't passed
- --setup
    - tells the app to build out the database infrastructure in the scripts folder and create the inQ and output directories. More details on this in [Setup Run section](#setup-run).
    - no other features of this app will run when --setup is passed

Examples:
```sh
-- setup the prod environment
pipenv run python program.py --mode prod --setup
```
```sh
-- process prod data
pipenv run python program.py --mode prod
```

### Intial Runs
#### Setup Run <a name="setup_run"></a>
As there are a lot of various tables, procs, and data loads to create in Snowflake, I've added a setup feature that automates this by running all sql scripts in your scripts folder. It also creates the inQ and output directories. This can be done by passing the --setup flag when running the app:
```sh
pipenv run python program.py --mode test --setup
```

Setup or not, the first run of this app will create the logs directory.

#### Categories Run
This is the tedious part. To categorize your transaction data, you need to map transaction descriptions to specific categories and load them to exp_categories. The matching is explicitly defined in a reference table because fuzzy matching runs into the issue of a single transaction mapping to multiple categories. There are services that will categorize the transactions automatically that I'd like to integrate with at some point.

To get a .csv file with all the uncategorized descriptions, run the app like normal and retrieve the file from the output folder:
```sh
pipenv run python program.py --mode test
```

AI can help A LOT with this. I fed Gemini a file with my transaction descriptions and a file with the categories I defined, and it did a pretty good job matching them.
If you want to use the categories I defined, they can be found in the categories table in your snowflake DB - assuming you've run --setup.

## Running the App
The app has 3 main functionalities that can be run modularly by setting the following to true or false in config.json:
```json
{
    "load_files":true,
    "update_categories":true,
    "refresh_gsheet":true,
    ...
}
```
They can be run individually or in any combination.

### Functionality
The following is a breakdown of what each functionality actually does
#### load_file
- loads any files in the inQ with a filename matching a file_pattern in config_log
- runs preprocessing on that file to:
    - apply any custom transformations to files defined in "preproc_files" in config.json
    - rename the fields of that file's dataframe based on "column_mappings" in config.json
    - apply standard transformation to any file such as removing symbols from transaction description
- pushes the transaction data to the raw table defined in config_log.raw_table
- runs the proc defined in config_log.stored_proc to standardize new data loaded to raw table and load it to the final table
- archives the file

#### update_categories
- runs proc defined in "categories_proc" in config.json to:
    - move credit payments to their own table and delete them from final table
    - update category in final table based on mapping defined in exp_categories
    - apply any custom recategorization 
    - return the number of final table record for which category was updated and the number of transaction descriptions matching to multiple categories (just a sanity check - should always be 0)
- runs proc defined in "uncategorized_proc" in config.json to return any uncategorized final table records
- writes records to a .csv file in output directory

**A note on credit payments:** Credit payments are removed because they would be redundant. This is because the app assumes you're already providing credit data on a transaction level so you don't need to track the payments themselves. Which transaction descriptions get flagged as credit payments and removed is defined in exp_exclusions where exclude_reason = 'credit payment'.

#### refresh_gsheet
- runs proc defined in "get_expenses_proc" in config.json to get all categorized records from the final table into a dataframe
- converts all dataframe nulls to empty strings and all fields to type string (google sheets can be finicky with other datatypes)
- deletes all data from Google sheet defined in "expense_sheet" in config.json
- loads dataframe to sheet

## Tableau Dashboard
Dashboard demo available on Tableau Public: https://public.tableau.com/views/expense_tracking_demo/expensemonitoring


Screenshots:


The dashboard provides:
- a monthly breakdown of expenses, revenue, and net income
- a granular, category level breakdown of expenses and revenues for the months specified in the transaction month filter
- a visual representation of these expenses by category is also available as a pie chart
- note that the transaction months filter applies to both the Monthly Expenses pie chart and the Monthly Expenses By Category crosstab
- a breakdown of expense categories by month for the categories specified in the filter

## Roadmap
- [x] Add support for multiple environments: test and prod
- [x] Automate data refreshes for Google Sheets by integrating with gspread
- [x] Set up a Tableau dashboard to visualize and aggregate the final financial data
- [ ] Beautify Tableau dashboard - it's very utilitarian
- [ ] Make app serverless: Dockerize and integrate with Snowpark Container Services
    - this opens a whole can of worms as far as getting the transaction data:
        - ideally, integrate with a financial data provider so it pulls from an API and doesn't need flat files
        - alternatively, integrate with AWS and Snowpipe: can load data to an S3 bucket and its immediately available in Snowflake
- [ ] integrate with either Plaid or SimpleFIN
    - Plaid will automate getting transaction data from banks/credit institutions and categorizing transactions
    - SimpleFIN will only automate getting transaction data but is quicker and easier to get started with
- [ ] Adapt the standarization procs from needing 1 proc per bank to having a dynamic proc template that can be fed tables/transformation/value configured for each bank