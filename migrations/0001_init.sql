-- pico.UP
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
DROP TABLE IF EXISTS test_table_gsi;
DROP TABLE IF EXISTS test_table;
