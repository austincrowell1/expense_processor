-- CALL stdz_bank1('bank 1');
CREATE OR REPLACE PROCEDURE stdz_bank1 (account_name VARCHAR(255))
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
        CAST(transaction_date as DATETIME) AS trans_date,
        description,
        CASE
            WHEN debit IS NULL THEN credit
            ELSE debit * -1
        END AS amount
    from raw_bank1
    where 1=1
    and insert_date > :last_proc_date;

    row_count := SQLROWCOUNT;
    
    UPDATE config_log
    SET last_process_date = CURRENT_TIMESTAMP()
    WHERE feed_name = :account_name;
    
    RETURN :account_name || ' rows inserted to cleansed_expenses: ' || :row_count;
    
END;
$$;
