use std::sync::LazyLock;

use shors::transport::{
    Context,
    http::{
        Request, Response,
        route::{Builder, Route},
        server::Server,
    },
};

use crate::index::{IndexIdentifier, add_index};

thread_local! {
    pub static HTTP_SERVER: LazyLock<Server> = LazyLock::new(Server::new);
}

#[must_use]
pub fn routes() -> Vec<Route<anyhow::Error>> {
    let add = Builder::new()
        .with_method("GET")
        .with_path("/add/:table_name")
        .build(|ctx: &mut Context, r: Request| -> anyhow::Result<()> {
            log::error!("ctx is {ctx:?}, request is {r:?}");
            let table_name = r.stash.get("table_name").unwrap().to_string();
            let id =
                IndexIdentifier::new(table_name, vec![String::from("b")], vec![String::from("a")]);
            log::error!("id is {id:?}");
            add_index(&id).unwrap();
            Ok(())
        });

    let search = Builder::new()
        .with_method("GET")
        .with_path("/search/:table_name")
        .build(|ctx: &mut Context, r: Request| -> anyhow::Result<()> {
            log::error!("ctx is {ctx:?}, request is {r:?}");
            let table_name = r.stash.get("table_name").unwrap().to_string();
            let id =
                IndexIdentifier::new(table_name, vec![String::from("b")], vec![String::from("a")]);
            // add_index(&id).unwrap();
            Ok(())
        });

    let insert = Builder::new()
        .with_method("GET")
        .with_path("/insert/:table_name")
        .build(|ctx: &mut Context, r: Request| -> anyhow::Result<()> {
            let table_name = r.stash.get("table_name").unwrap().to_string();
            let id =
                IndexIdentifier::new(table_name, vec![String::from("b")], vec![String::from("a")]);
            log::error!("ctx is {ctx:?}, request is {r:?}");
            log::error!("id is {id:?}");
            // add_index(&id).unwrap();
            Ok(())
        });

    vec![add, search, insert]
}
