use crate::index::{DistributionType, IndexIdentifier};

pub mod in_memory {
    use std::{
        cell::LazyCell,
        collections::{BTreeMap, HashMap},
    };

    use crate::bucket::Value;

    thread_local! {
        pub static INDEXES: LazyCell<HashMap<String, BTreeMap<Value, Value>>> =
            LazyCell::new(|| HashMap::with_capacity(16));
    }

    /// Become a scatter-gather manager to ensure that the index was built
    /// on every replicaset leader of the cluster.
    pub fn add_index() {}

    pub fn build_on_instance() {}
}

pub mod in_table {}
