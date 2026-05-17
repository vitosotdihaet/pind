use picodata_plugin::system::tarantool::log as t_log;

use std::str::FromStr;
use std::sync::LazyLock;

const ALL_LOGS_ERROR: bool = false;

static LOGGER: LazyLock<t_log::TarantoolLogger> = LazyLock::new(|| {
    if ALL_LOGS_ERROR {
        t_log::TarantoolLogger::with_mapping(|level: log::Level| match level {
            log::Level::Error
            | log::Level::Warn
            | log::Level::Info
            | log::Level::Debug
            | log::Level::Trace => t_log::SayLevel::Error,
        })
    } else {
        t_log::TarantoolLogger::with_mapping(|level: log::Level| match level {
            log::Level::Error => t_log::SayLevel::Error,
            log::Level::Warn => t_log::SayLevel::Warn,
            log::Level::Info => t_log::SayLevel::Info,
            log::Level::Debug => t_log::SayLevel::Verbose,
            log::Level::Trace => t_log::SayLevel::Debug,
        })
    }
});

pub fn init_logger() {
    if let Err(e) = log::set_logger(&*LOGGER) {
        println!("failed to setup logger: {e:?}");
    }
    log::set_max_level(log::LevelFilter::Info);
    let Ok(log_level_str) = std::env::var("PICODATA_LOG_LEVEL") else {
        return;
    };
    let Ok(log_level) = log::LevelFilter::from_str(&log_level_str) else {
        return;
    };
    if ALL_LOGS_ERROR {
        log::set_max_level(log::LevelFilter::Trace);
    } else {
        log::set_max_level(log_level);
    }
}
