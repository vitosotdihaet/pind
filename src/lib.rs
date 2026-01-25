mod log;
mod metrics;
mod scrape;
mod search;

use picodata_plugin::plugin::{interface::ServiceRegistry, prelude::service_registrar};

#[service_registrar]
pub fn service_registrar(reg: &mut ServiceRegistry) {
    reg.add(
        "search",
        env!("CARGO_PKG_VERSION"),
        search::service::Search::default,
    );
    reg.add(
        "scrape",
        env!("CARGO_PKG_VERSION"),
        scrape::service::Scrape::default,
    );
    reg.add_config_validator::<scrape::service::Scrape>(
        "scrape",
        env!("CARGO_PKG_VERSION"),
        |cfg| Ok(cfg.validate()?),
    );
}
