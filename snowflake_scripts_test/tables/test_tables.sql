CREATE OR REPLACE TABLE config_log(
    id INT IDENTITY(1,1) PRIMARY KEY,
    feed_name VARCHAR(255),
    last_process_date DATETIME,
    file_pattern VARCHAR(255),
    stored_proc VARCHAR(255),
    raw_table VARCHAR(255),
    final_table VARCHAR(255)
);

CREATE OR REPLACE TABLE raw_bank1(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    transaction_date VARCHAR(255),
    posted_date VARCHAR(255),
    card_no VARCHAR(255),
    description VARCHAR(255),
    category VARCHAR(255),
    debit VARCHAR(255),
    credit VARCHAR(255)
);

CREATE OR REPLACE TABLE raw_bank23(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    account_type VARCHAR(255) DEFAULT NULL,
    trans_date VARCHAR(255),
    trans_time VARCHAR(255),
    amount VARCHAR(255),
    trans_type VARCHAR(255),
    description VARCHAR(255)
);

CREATE OR  REPLACE TABLE raw_bank4(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    trans_date VARCHAR(255),
    description VARCHAR(255),
    amount VARCHAR(255),
    running_bal VARCHAR(255)
);

CREATE OR  REPLACE TABLE raw_bank5(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    account_type VARCHAR(255) DEFAULT NULL,
    trans_date VARCHAR(255),
    post_date VARCHAR(255),
    description VARCHAR(255),
    amount VARCHAR(255),
    category VARCHAR(255)
);

CREATE OR  REPLACE TABLE raw_bank6(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    trans_date VARCHAR(255),
    post_date VARCHAR(255),
    description VARCHAR(255),
    category VARCHAR(255),
    trans_type VARCHAR(255),
    amount VARCHAR(255),
    memo VARCHAR(255)
);

CREATE OR REPLACE TABLE cleansed_expenses(
    id INT IDENTITY(1,1) PRIMARY KEY,
    raw_table_id INT NOT NULL,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    bank_name VARCHAR(255),
    trans_date DATETIME,
    description VARCHAR(255),
    category VARCHAR(255),
    amount NUMBER(38,2)
);

CREATE OR REPLACE TABLE credit_payments(
    id INT IDENTITY(1,1) PRIMARY KEY,
    raw_table_id INT NOT NULL,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    bank_name VARCHAR(255),
    trans_date DATETIME,
    description VARCHAR(255),
    category VARCHAR(255),
    amount NUMBER(38,2)
);

create or replace table exp_categories(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    category VARCHAR(255),
    keyword VARCHAR(255)
);

CREATE OR REPLACE TABLE exp_exclusions(
    id INT IDENTITY(1,1) PRIMARY KEY,
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP(),
    feed_name VARCHAR(255),
    description VARCHAR(255),
    exclude_reason VARCHAR(255)
);

