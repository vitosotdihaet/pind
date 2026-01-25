use crate::search::config;

use crate::search::endpoints::http::{HTTP_SERVER, routes};
use crate::search::endpoints::rpc::register_rpc_handlers;
use picodata_plugin::plugin::prelude::*;

#[derive(Debug, Default)]
pub struct Search {}

impl Service for Search {
    type Config = config::SearchConfig;

    fn on_config_change(
        &mut self,
        ctx: &PicoContext,
        new_config: Self::Config,
        old_config: Self::Config,
    ) -> CallbackResult<()> {
        _ = ctx;
        _ = new_config;
        _ = old_config;

        Ok(())
    }

    fn on_start(&mut self, ctx: &PicoContext, config: Self::Config) -> CallbackResult<()> {
        _ = config;

        crate::log::init_logger();

        log::info!("registering HTTP handles for search");
        HTTP_SERVER.with(|srv| {
            routes()
                .into_iter()
                .for_each(|route| srv.register(Box::new(route)));
        });

        log::info!("registering RPC handles for search");
        register_rpc_handlers(ctx);

        if let Err(e) = ctx.register_metrics_callback(crate::metrics::collect) {
            log::error!("could not start the /metrics endpoint, reason: {e:?}");
        }

        Ok(())
    }

    fn on_stop(&mut self, ctx: &PicoContext) -> CallbackResult<()> {
        _ = ctx;
        Ok(())
    }

    fn on_leader_change(&mut self, ctx: &PicoContext) -> CallbackResult<()> {
        _ = ctx;
        Ok(())
    }

    fn on_health_check(&self, ctx: &PicoContext) -> CallbackResult<()> {
        _ = ctx;
        Ok(())
    }
}
