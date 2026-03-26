-- CALL update_categories()
CREATE OR REPLACE PROCEDURE update_categories()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE dupe_num INT;
BEGIN

    -- move credit card payments to their own table
    INSERT into credit_payments(
        raw_table_id,
        bank_name,
        trans_date,
        description,
        amount
    )
    SELECT
        a.raw_table_id,
        a.bank_name,
        a.trans_date,
        a.description,
        a.amount
    FROM cleansed_expenses a
    JOIN exp_exclusions b
        ON a.bank_name = b.feed_name
        AND a.description = b.description
    WHERE b.exclude_reason = 'credit payment';

    delete 
    --select *
    from cleansed_expenses a
    where description in (
        select description
        from exp_exclusions b
        where a.bank_name = b.feed_name
        AND a.description = b.description
    );
    
    -- dedupe to verify transactions aren't matching to multiple categories
    CREATE OR REPLACE TEMPORARY TABLE dedupe AS
    SELECT
        a.id,
        a.description,
        a.amount,
        b.category,
        ROW_NUMBER() OVER (PARTITION BY a.id ORDER BY b.category) as rownum
    FROM cleansed_expenses a
    JOIN exp_categories b
        ON a.description = b.keyword
    WHERE a.category IS NULL;

    SELECT COUNT(DISTINCT id)
    into :dupe_num 
    FROM dedupe WHERE rownum > 1;

    -- for sams club under $40, set to gas. otherwise keep default (groceries)
    UPDATE dedupe
    SET category = 'gas'
    WHERE category = 'groceries & home goods'
    AND description ilike '%sams%'
    AND NOT REGEXP_LIKE(description, '.*(walmart|scanngo|renewal).*', 'i')
    AND amount > -40;

    MERGE INTO cleansed_expenses a
    USING (SELECT id, category FROM dedupe WHERE rownum = 1) b
    ON a.id = b.id
    WHEN MATCHED AND a.category IS NULL THEN
    UPDATE SET 
        a.category = b.category,
        a.modify_date = CURRENT_TIMESTAMP();

    RETURN 'rows updated: ' || SQLROWCOUNT || ', dupes found: ' || dupe_num;
    
END;
$$;