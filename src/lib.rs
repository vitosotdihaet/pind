pub mod bucket;
mod config;
mod endpoints;
mod index;
mod log;
mod metrics;
pub mod repo;
mod service;

use picodata_plugin::plugin::{interface::ServiceRegistry, prelude::service_registrar};

use crate::service::Pind;

#[service_registrar]
pub fn service_registrar(reg: &mut ServiceRegistry) {
    reg.add("pind", env!("CARGO_PKG_VERSION"), Pind::new);
}
