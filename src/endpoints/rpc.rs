use picodata_plugin::transport::rpc;
use picodata_plugin::{plugin::prelude::*, transport::rpc::RouteBuilder};
// use serde::{Deserialize, Serialize};

pub fn register_rpc_handlers(context: &PicoContext) {
    RouteBuilder::from_pico_context(context)
        .path("/greetings_rpc")
        .register(move |req, _ctx| {
            log::error!("got request {req:?} in /greetings_rpc");
            Ok(rpc::Response::encode_rmp(&()).unwrap())
        })
        .unwrap();
}
