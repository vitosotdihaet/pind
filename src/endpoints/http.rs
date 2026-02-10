use std::{collections::HashMap, sync::LazyLock};

use shors::transport::{
    Context,
    http::{
        Request, Response,
        route::{Builder, Route},
        server::Server,
    },
};

thread_local! {
    pub static HTTP_SERVER: LazyLock<Server> = LazyLock::new(Server::new);
}

#[must_use]
pub fn routes() -> Vec<Route<anyhow::Error>> {
    let search_route = Builder::new()
        .with_method("GET")
        .with_path("/search/:text")
        .build(|_: &mut Context, r: Request| -> anyhow::Result<_> {
            let text = r
                .stash
                .get("text")
                .expect("can't access this endpoint without the text part");

            let res = ();
            let message = format!("Bro, you are looking for {text}? Here's the result: {res:?}");

            Ok(Response {
                status: 200,
                headers: HashMap::from([(
                    "content-type".to_string(),
                    "text/plain; charset=utf8".to_string(),
                )]),
                body: message.as_bytes().to_vec(),
            })
        });

    vec![search_route]
}
