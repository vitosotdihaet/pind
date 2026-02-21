mod global;
mod local;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Hash)]
pub enum DistributionType {
    Global,
    Local,
}

#[derive(Debug, Serialize, Deserialize, Hash)]
pub enum PersistenceType {
    Memory,
    Table,
}

#[derive(Debug, Serialize, Deserialize, Hash)]
pub struct IndexIdentifier {
    table_name: String,
    column_names: Vec<String>,
    distribution: DistributionType,
    persistence: PersistenceType,
}

impl IndexIdentifier {
    pub fn new(
        table_name: String,
        column_names: Vec<String>,
        distribution: DistributionType,
        persistence: PersistenceType,
    ) -> IndexIdentifier {
        IndexIdentifier {
            table_name,
            column_names,
            distribution,
            persistence,
        }
    }
}

/// Add an index entry to _pind_indexes, then build the index.
pub fn add_index(identifier: &IndexIdentifier) -> Result<(), ()> {
    Ok(())
}
