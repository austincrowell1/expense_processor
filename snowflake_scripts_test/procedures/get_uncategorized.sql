-- call get_uncategorized()
CREATE OR REPLACE PROCEDURE get_uncategorized()
RETURNS TABLE()
LANGUAGE SQL
AS
$$
DECLARE
    uncat_results RESULTSET;
    
BEGIN
    uncat_results := (
        SELECT
            ID,
            RAW_TABLE_ID,
            INSERT_DATE,
            MODIFY_DATE,
            BANK_NAME,
            TRANS_DATE,
            DESCRIPTION,
            '' as category,
            AMOUNT
        FROM cleansed_expenses
        WHERE category is null
    );

    RETURN TABLE(uncat_results);
END;
$$;