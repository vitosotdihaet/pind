-- pico.UP
CREATE TABLE IF NOT EXISTS _pind_indexes (
    table_name: TEXT,
    column_names: TEXT, -- binary representation
    distribution: TEXT,
    persistence: TEXT,
    PRIMARY KEY (table_name, column_name, distribution, persistence)
) USING memtx DISTRIBUTED GLOBALLY WAIT APPLIED GLOBALLY;

-- pico.DOWN
DROP TABLE IF EXISTS _pind_indexes;