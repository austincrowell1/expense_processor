INSERT INTO config_log(
    feed_name,
    last_process_date,
    file_pattern,
    stored_proc,
    raw_table,
    final_table
)
VALUES
    ('bank 1','1900-01-01', 'bank1_*.csv', 'stdz_bank1', 'raw_bank1', 'cleansed_expenses'),
    ('bank 2','1900-01-01', 'bank2_*.csv', 'stdz_bank23', 'raw_bank23', 'cleansed_expenses'),
    ('bank 3','1900-01-01', 'bank3_*.csv', 'stdz_bank23', 'raw_bank23', 'cleansed_expenses'),
    ('bank 4','1900-01-01', 'bank4_*.csv', 'stdz_bank4', 'raw_bank4', 'cleansed_expenses'),
    ('bank 5','1900-01-01', 'bank5_*.csv', 'stdz_bank5', 'raw_bank5', 'cleansed_expenses')
;

insert into exp_exclusions (feed_name, description, exclude_reason) 
values 
    ('bank 1', 'bank 1 test record 2','test exclusion'),
    ('bank 2', 'bank 2 test record 1','test exclusion')
;

insert into exp_categories(keyword, category)
values
    ('bank 1 test record 1','bank 1 test cat'),
    ('bank 1 test record 2','bank 1 test cat'),
    ('bank 1 test record 3','bank 1 test cat'),
    ('bank 1 test record 4','bank 1 test cat'),
    ('bank 1 test record 5','bank 1 test cat'),
    ('bank 2 test record 1','bank 2 test cat'),
    ('bank 2 test record 2','bank 2 test cat'),
    ('bank 2 test record 3','bank 2 test cat'),
    ('bank 2 test record 4','bank 2 test cat'),
    ('bank 2 test record 5','bank 2 test cat'),
    ('bank 3 test record 1','bank 3 test cat'),
    ('bank 3 test record 2','bank 3 test cat'),
    ('bank 3 test record 3','bank 3 test cat'),
    ('bank 3 test record 4','bank 3 test cat'),
    ('bank 3 test record 5','bank 3 test cat'),
    ('bank 4 test record 1','bank 4 test cat'),
    -- ('bank 4 test record 2','bank 4 test cat'),
    ('bank 4 test record 3','bank 4 test cat'),
    ('bank 4 test record 4','bank 4 test cat'),
    ('bank 5 test record 1','bank 5 test cat'),
    ('bank 5 test record 2','bank 5 test cat'),
    ('bank 5 test record 3','bank 5 test cat'),
    -- ('bank 5 test record 4','bank 5 test cat'),
    ('bank 5 test record 5','bank 5 test cat')
;