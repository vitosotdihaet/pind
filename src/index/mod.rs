use picodata_plugin::sql::{self, query_raw, types::SqlValue};
use serde::{Deserialize, Serialize};
use shors::tarantool::msgpack::Decode;

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

const TABLE_NAME: &'static str = "test_table";
const GSI_NAME: &'static str = "test_table_gsi";

// /// Add an index entry to _pind_indexes, then build the index.
// pub fn add_index(identifier: &IndexIdentifier) -> Result<(), ()> {
//     let table_name = format!("{}_gsi", identifier.table_name);
//     let mut params = Vec::new();
//     params.push(table_name.into());
//     params.append(
//         &mut identifier
//             .column_names
//             .clone()
//             .into_iter()
//             .map(|c| c.into())
//             .collect::<Vec<SqlValue>>(),
//     );
//     params.append(
//         &mut identifier
//             .primary_key_column_names
//             .clone()
//             .into_iter()
//             .map(|c| c.into())
//             .collect::<Vec<SqlValue>>(),
//     );
//     params.append(
//         &mut identifier
//             .column_names
//             .clone()
//             .into_iter()
//             .map(|c| c.into())
//             .collect::<Vec<SqlValue>>(),
//     );

//     let columns_string = identifier
//         .column_names
//         .iter()
//         .map(|_| String::from("? int"))
//         .collect::<Vec<_>>()
//         .join(", ");

//     let primary_key_string = identifier
//         .primary_key_column_names
//         .iter()
//         .map(|_| String::from("?"))
//         .collect::<Vec<_>>()
//         .join(", ");

//     let columns_string_no_types = identifier
//         .column_names
//         .iter()
//         .map(|_| String::from("?"))
//         .collect::<Vec<_>>()
//         .join(", ");

//     let query = format!(
//         r#"CREATE TABLE IF NOT EXISTS ? ({}, primary key ({})) distributed by ({}) in tier pind;"#,
//         columns_string, primary_key_string, columns_string_no_types
//     );
//     log::debug!("query is {query}");

//     let q = picodata_plugin::sql::query_raw(query.as_str(), params);

//     log::debug!("q is {q:#?}");
//     q.unwrap();

//     Ok(())
// }

#[derive(Deserialize, Debug)]
pub struct PkSk {
    pk: String,
    sk: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Row {
    pk: String,
    fk: String,
    sk: String,
}

pub fn search_gsi(fk: &str) -> anyhow::Result<Vec<Row>> {
    let query_text = format!(r#"SELECT pk, sk FROM {GSI_NAME} WHERE fk = ?"#);
    let pksks: Vec<_> = sql::query(&query_text)
        .bind(fk)
        .fetch::<PkSk>()
        .map_err(|e| anyhow::anyhow!(e))?
        .into_iter()
        .collect();

    log::debug!("got pksks = {pksks:?}");

    let where_template = String::from("(pk = ? AND sk = ?)");

    let where_clause = pksks
        .iter()
        .map(|_| where_template.clone())
        .collect::<Vec<String>>()
        .join(" OR ");

    let query_text = format!(r#"SELECT pk, fk, sk FROM {TABLE_NAME} WHERE {where_clause}"#);
    log::debug!("query_text = {query_text:?}");
    let mut q = sql::query(&query_text);
    for pksk in pksks {
        q = q.bind(pksk.pk).bind(pksk.sk);
    }
    let rows: Vec<_> = q
        .fetch::<Row>()
        .map_err(|e| anyhow::anyhow!(e))?
        .into_iter()
        .collect();

    Ok(rows)
}

pub fn insert_gsi(row: &Row) -> anyhow::Result<u64> {
    let query_text = format!(r#"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?)"#);
    let inserted = sql::query(&query_text)
        .bind(row.pk.clone())
        .bind(row.fk.clone())
        .bind(row.sk.clone())
        .execute()
        .map_err(|e| anyhow::anyhow!(e))?;

    log::debug!("got inserted into table = {inserted:?}");

    let query_text = format!(r#"INSERT INTO {GSI_NAME} VALUES (?, ?, ?)"#);
    let inserted_gsi = sql::query(&query_text)
        .bind(row.fk.clone())
        .bind(row.pk.clone())
        .bind(row.sk.clone())
        .execute()
        .map_err(|e| anyhow::anyhow!(e))?;

    log::debug!("got inserted into gsi = {inserted_gsi:?}");

    Ok(inserted)
}

pub fn search_lsi(fk: &str) -> anyhow::Result<Vec<Row>> {
    let query_text = format!(r#"SELECT pk, fk, sk FROM {TABLE_NAME} WHERE fk = ?"#);
    log::debug!("query_text = {query_text:?}");
    let q = sql::query(&query_text).bind(fk);

    let rows: Vec<_> = q
        .fetch::<Row>()
        .map_err(|e| anyhow::anyhow!(e))?
        .into_iter()
        .collect();

    Ok(rows)
}

pub fn insert_lsi(row: &Row) -> anyhow::Result<u64> {
    let query_text = format!(r#"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?)"#);
    let inserted = sql::query(&query_text)
        .bind(row.pk.clone())
        .bind(row.fk.clone())
        .bind(row.sk.clone())
        .execute()
        .map_err(|e| anyhow::anyhow!(e))?;

    Ok(inserted)
}
