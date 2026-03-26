-- CALL stdz_bank23('bank 2');
-- CALL stdz_bank23('bank 3');
CREATE OR REPLACE PROCEDURE stdz_bank23 (account_name VARCHAR(255))
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE 
    last_proc_date DATETIME;
    row_count INT;
BEGIN
    
    -- get delta processing date
    SELECT top 1
        last_process_date
    into :last_proc_date
    FROM config_log
    WHERE feed_name = :account_name;

    -- update the raw table account type to differentiate checking vs savings
    UPDATE raw_bank23
    SET account_type = :account_name
    where insert_date > :last_proc_date
    and account_type is null;
    
    INSERT INTO cleansed_expenses(
        raw_table_id,
        bank_name,
        trans_date,
        description,
        amount
    )
    SELECT
        id,
        :account_name,
        CAST(trans_date AS DATETIME) AS trans_date,
        description,
        CAST(amount AS NUMBER(38,2)) AS amount
    FROM raw_bank23
    where 1=1
    and account_type = :account_name
    and insert_date > :last_proc_date;

    row_count := SQLROWCOUNT;

    UPDATE config_log
    SET last_process_date = CURRENT_TIMESTAMP()
    WHERE feed_name = :account_name;

    RETURN :account_name || ' rows inserted to cleansed_expenses: ' || :row_count;
    
END;
$$;