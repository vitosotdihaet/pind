-- pico.UP
CREATE TABLE IF NOT EXISTS _pind_indexes (
    table_name TEXT,
    column_names TEXT, -- binary representation
    distribution TEXT,
    persistence TEXT,
    PRIMARY KEY (table_name, column_names, distribution, persistence)
) USING memtx DISTRIBUTED GLOBALLY WAIT APPLIED GLOBALLY;

CREATE TABLE IF NOT EXISTS test_table (
    pk TEXT PRIMARY KEY,
    fk TEXT,
    sk TEXT
) USING memtx DISTRIBUTED BY ("sk") IN TIER pind WAIT APPLIED GLOBALLY;

CREATE TABLE IF NOT EXISTS test_table_gsi (
    fk TEXT,
    pk TEXT,
    sk TEXT,
    PRIMARY KEY (fk, pk)
) USING memtx DISTRIBUTED BY ("fk") IN TIER pind WAIT APPLIED GLOBALLY;


-- pico.DOWN
DROP TABLE IF EXISTS test_table;
DROP TABLE IF EXISTS _pind_indexes;
