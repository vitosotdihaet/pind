mod config;
mod handlers;
mod service;

use picodata_plugin::plugin::{interface::ServiceRegistry, prelude::service_registrar};

#[service_registrar]
pub fn service_registrar(reg: &mut ServiceRegistry) {
    reg.add(
        "search",
        env!("CARGO_PKG_VERSION"),
        service::Search::default,
    );
    // reg.add_config_validator::<service::ExampleService>("pind", env!("CARGO_PKG_VERSION"), |cfg| {
    //     if let Some(cfg_value) = cfg.value {
    //         if cfg_value == "tarantool" {
    //             return Err("Please call a pest control service!".into());
    //         }
    //     }
    //     Ok(())
    // });
}
