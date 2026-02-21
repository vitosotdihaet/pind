use std::sync::LazyLock;

use shors::transport::{
    Context,
    http::{
        Request, Response,
        route::{Builder, Route},
        server::Server,
    },
};

use crate::index::{DistributionType, IndexIdentifier, PersistenceType, add_index};

thread_local! {
    pub static HTTP_SERVER: LazyLock<Server> = LazyLock::new(Server::new);
}

#[must_use]
pub fn routes() -> Vec<Route<anyhow::Error>> {
    let search_route = Builder::new()
        .with_method("GET")
        .with_path("/add/:table_name")
        .build(|ctx: &mut Context, r: Request| -> anyhow::Result<()> {
            log::debug!("ctx is {ctx:?}, request is {r:?}");
            let id = IndexIdentifier::new(
                String::from("_pind_test_table"),
                vec![String::from("a")],
                DistributionType::Local,
                PersistenceType::Memory,
            );
            add_index(&id).unwrap();
            Ok(())
        });

    vec![search_route]
}
