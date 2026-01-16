-- pico.UP
create table if not exists "_pind_terms" (
    term TEXT NOT NULL,
    ptr_lvl_0 TEXT NOT NULL,
) USING memtx DISTRIBUTED BY ("term") IN tier @_plugin_config.tier_0 WAIT APPLIED LOCALLY OPTION (TIMEOUT = 3.0);

CREATE TABLE IF NOT EXISTS "_pind_lvls" (
    ptr TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    ptr_lvl_0 TEXT,
    ptr_lvl_1 TEXT NULL,
    ptr_lvl_2 TEXT NULL,
) USING memtx DISTRIBUTED BY ("ptr") IN tier @_plugin_config.tier_0 WAIT APPLIED LOCALLY OPTION (TIMEOUT = 3.0);
-- the table is actually distributed by a term of these pointers

-- pico.DOWN
