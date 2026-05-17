use std::sync::LazyLock;

use serde::Deserialize;
use shors::transport::{
    Context,
    http::{
        Request,
        route::{Builder, Route},
        server::Server,
    },
};

use crate::index::{Row, insert_gsi, insert_lsi, search_gsi, search_lsi};

thread_local! {
    pub static HTTP_SERVER: LazyLock<Server> = LazyLock::new(Server::new);
}

#[must_use]
pub fn routes() -> Vec<Route<anyhow::Error>> {
    let search_gsi = Builder::new()
        .with_method("POST")
        .with_path("/search_gsi")
        .build(
            |_ctx: &mut Context, r: Request| -> anyhow::Result<Vec<Row>> {
                #[derive(Deserialize, Debug)]
                struct SearchValue {
                    fk: String,
                }

                let res = r.parse();
                let value: SearchValue = res?;
                let rows = search_gsi(&value.fk).unwrap_or_else(|e| {
                    log::error!("res rows got error: {e:?}");
                    Vec::default()
                });

                Ok(rows)
            },
        );

    let insert_gsi = Builder::new()
        .with_method("POST")
        .with_path("/insert_gsi")
        .build(|_ctx: &mut Context, r: Request| -> anyhow::Result<u64> {
            let row: Row = r.parse()?;
            let res = insert_gsi(&row).unwrap_or_else(|e| {
                log::error!("res insert got error: {e:?}");
                0
            });

            Ok(res)
        });

    let search_lsi = Builder::new()
        .with_method("POST")
        .with_path("/search_lsi")
        .build(
            |_ctx: &mut Context, r: Request| -> anyhow::Result<Vec<Row>> {
                #[derive(Deserialize, Debug)]
                struct SearchValue {
                    fk: String,
                }

                let res = r.parse();
                let value: SearchValue = res?;
                let rows = search_lsi(&value.fk).unwrap_or_else(|e| {
                    log::error!("res rows got error: {e:?}");
                    Vec::default()
                });

                Ok(rows)
            },
        );

    let insert_lsi = Builder::new()
        .with_method("POST")
        .with_path("/insert_lsi")
        .build(|_ctx: &mut Context, r: Request| -> anyhow::Result<u64> {
            let row: Row = r.parse()?;
            let res = insert_lsi(&row).unwrap_or_else(|e| {
                log::error!("res insert got error: {e:?}");
                0
            });

            Ok(res)
        });

    vec![search_gsi, insert_gsi, search_lsi, insert_lsi]
}
