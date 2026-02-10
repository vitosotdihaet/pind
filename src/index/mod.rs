mod global;
mod local;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Hash)]
enum DistributionType {
    Global,
    Local,
}

#[derive(Debug, Serialize, Deserialize, Hash)]
enum PersistenceType {
    Memory,
    Table,
}

#[derive(Debug, Serialize, Deserialize, Hash)]
struct IndexIdentifier {
    table_name: String,
    column_names: Vec<String>,
    distribution: DistributionType,
    persistence: PersistenceType,
}
