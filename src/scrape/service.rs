use crate::scrape::config;

use crate::scrape::endpoints::rpc::register_rpc_handlers;
use picodata_plugin::plugin::prelude::*;

#[derive(Debug, Default)]
pub struct Scrape {}

impl Service for Scrape {
    type Config = config::ScrapeConfig;

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

        log::info!("registering RPC handlers for scrape");
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
