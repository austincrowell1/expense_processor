-- call get_cleansed_expenses()
CREATE OR REPLACE PROCEDURE get_cleansed_expenses()
RETURNS TABLE()
LANGUAGE SQL
AS
$$
DECLARE
    RESULTS RESULTSET;
    
BEGIN
    RESULTS := (
        SELECT
            CAST(ID AS INT) AS ID,
            CAST(RAW_TABLE_ID AS INT) AS RAW_TABLE_ID,
            INSERT_DATE,
            MODIFY_DATE,
            BANK_NAME,
            TRANS_DATE,
            DESCRIPTION,
            CATEGORY,
            AMOUNT
        FROM CLEANSED_EXPENSES
    );

    RETURN TABLE(RESULTS);
END;
$$;