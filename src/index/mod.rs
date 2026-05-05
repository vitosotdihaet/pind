use picodata_plugin::sql::types::SqlValue;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Hash)]
pub struct IndexIdentifier {
    table_name: String,
    column_names: Vec<String>,
    primary_key_column_names: Vec<String>,
}

impl IndexIdentifier {
    pub fn new(
        table_name: String,
        column_names: Vec<String>,
        primary_key_column_names: Vec<String>,
    ) -> IndexIdentifier {
        IndexIdentifier {
            table_name,
            column_names,
            primary_key_column_names,
        }
    }
}

/// Add an index entry to _pind_indexes, then build the index.
pub fn add_index(identifier: &IndexIdentifier) -> Result<(), ()> {
    let table_name = format!("{}_fk", identifier.table_name);
    let mut params = Vec::new();
    params.push(table_name.into());
    params.append(
        &mut identifier
            .column_names
            .clone()
            .into_iter()
            .map(|c| c.into())
            .collect::<Vec<SqlValue>>(),
    );
    params.append(
        &mut identifier
            .primary_key_column_names
            .clone()
            .into_iter()
            .map(|c| c.into())
            .collect::<Vec<SqlValue>>(),
    );
    params.append(
        &mut identifier
            .column_names
            .clone()
            .into_iter()
            .map(|c| c.into())
            .collect::<Vec<SqlValue>>(),
    );

    let columns_string = identifier
        .column_names
        .iter()
        .map(|_| String::from("? int"))
        .collect::<Vec<_>>()
        .join(", ");

    let primary_key_string = identifier
        .primary_key_column_names
        .iter()
        .map(|_| String::from("?"))
        .collect::<Vec<_>>()
        .join(", ");

    let columns_string_no_types = identifier
        .column_names
        .iter()
        .map(|_| String::from("?"))
        .collect::<Vec<_>>()
        .join(", ");

    let query = format!(
        r#"CREATE TABLE IF NOT EXISTS ? ({}, primary key ({})) distributed by ({}) in tier pind;"#,
        columns_string, primary_key_string, columns_string_no_types
    );
    log::debug!("query is {query}");

    let q = picodata_plugin::sql::query_raw(query.as_str(), params);

    log::debug!("q is {q:#?}");
    q.unwrap();

    Ok(())
}
