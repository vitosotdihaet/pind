use picodata_plugin::plugin::prelude::*;

use crate::{
    config::PindConfig,
    endpoints::{
        http::{HTTP_SERVER, routes},
        rpc::register_rpc_handlers,
    },
};

#[derive(Debug, Default)]
pub struct Pind {}

impl Pind {
    pub fn new() -> Pind {
        crate::log::init_logger();
        Pind {}
    }
}

impl Service for Pind {
    type Config = PindConfig;

    fn on_start(&mut self, ctx: &PicoContext, config: Self::Config) -> CallbackResult<()> {
        log::info!("pind on_start callback begin");
        _ = config;

        crate::bucket::set_bucket_event_listener();

        log::info!("registering HTTP handles for pind");
        HTTP_SERVER.with(|srv| {
            routes()
                .into_iter()
                .for_each(|route| srv.register(Box::new(route)));
        });

        log::info!("registering RPC handles for pind");
        register_rpc_handlers(ctx);

        if let Err(e) = ctx.register_metrics_callback(crate::metrics::collect) {
            log::error!("could not start the /metrics endpoint, reason: {e:?}");
        }

        log::info!("pind on_start callback end");
        Ok(())
    }

    fn on_stop(&mut self, ctx: &PicoContext) -> CallbackResult<()> {
        log::info!("pind on_stop callback begin");
        _ = ctx;
        log::info!("pind on_stop callback end");
        Ok(())
    }

    fn on_config_change(
        &mut self,
        ctx: &PicoContext,
        new_config: Self::Config,
        old_config: Self::Config,
    ) -> CallbackResult<()> {
        log::info!("pind on_config_change callback begin");
        _ = ctx;
        _ = new_config;
        _ = old_config;

        log::info!("pind on_config_change callback end");
        Ok(())
    }

    fn on_leader_change(&mut self, ctx: &PicoContext) -> CallbackResult<()> {
        log::info!("pind on_leader_change callback begin");
        _ = ctx;
        log::info!("pind on_leader_change callback end");
        Ok(())
    }

    fn on_health_check(&self, ctx: &PicoContext) -> CallbackResult<()> {
        log::info!("pind on_health_check callback begin");
        _ = ctx;
        log::info!("pind on_health_check callback end");
        Ok(())
    }
}
