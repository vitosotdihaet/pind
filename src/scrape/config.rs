use std::collections::HashMap;

use anyhow::Result;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum ScrapeConfigValidationError {
    #[error("get_from: {from} is after get_to: {to}")]
    GetTimeIsBad {
        from: DateTime<Utc>,
        to: DateTime<Utc>,
    },
    #[error("the queue_limit is zero")]
    QueueLimitIsZero,
}

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct ScrapeConfig {
    sites: HashMap<String, SiteScrapeConfig>,
}

impl ScrapeConfig {
    pub fn validate(&self) -> Result<()> {
        for (_k, v) in self.sites.iter() {
            v.validate()?;
        }

        Ok(())
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SiteScrapeConfig {
    crawl_delay_sec: u64,
    get_from: DateTime<Utc>,
    get_to: DateTime<Utc>,
    queue_limit: usize,
}

impl Default for SiteScrapeConfig {
    fn default() -> Self {
        Self {
            crawl_delay_sec: Default::default(),
            get_from: DateTime::<Utc>::MIN_UTC,
            get_to: DateTime::<Utc>::MAX_UTC,
            queue_limit: Default::default(),
        }
    }
}

impl SiteScrapeConfig {
    pub fn validate(&self) -> Result<()> {
        if self.crawl_delay_sec == 0 {
            log::warn!("SiteScrapeConfig::crawl_delay_sec is zero!");
        }

        if self.get_from >= self.get_to {
            return Err(ScrapeConfigValidationError::GetTimeIsBad {
                from: self.get_from.clone(),
                to: self.get_to.clone(),
            }
            .into());
        }

        if self.queue_limit == 0 {
            return Err(ScrapeConfigValidationError::QueueLimitIsZero.into());
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use std::str::FromStr;

    use chrono::DateTime;

    use crate::scrape::config::{ScrapeConfig, ScrapeConfigValidationError, SiteScrapeConfig};

    #[test]
    fn empty_config_to_yaml() {
        let s = ScrapeConfig::default();
        let str = serde_yaml::to_string(&s).unwrap();
        let expected = "sites: {}\n";
        assert_eq!(str, expected);
    }

    #[test]
    fn validate_config_get_time() {
        let mut cfg = ScrapeConfig::default();

        let site_cfg = SiteScrapeConfig {
            crawl_delay_sec: 123,
            get_from: DateTime::from_str("1984-01-01T12:34:56+00:00").unwrap(),
            get_to: DateTime::from_str("1983-01-01T12:34:56+00:00").unwrap(),
            queue_limit: 123,
        };
        let expected_err = ScrapeConfigValidationError::GetTimeIsBad {
            from: site_cfg.get_from,
            to: site_cfg.get_to,
        };

        let err = site_cfg.validate().unwrap_err().downcast().unwrap();
        assert_eq!(expected_err, err);

        cfg.sites.insert(String::from("some_site"), site_cfg);

        let err = cfg.validate().unwrap_err().downcast().unwrap();
        assert_eq!(expected_err, err);
    }

    #[test]
    fn validate_config_queue() {
        let mut cfg = ScrapeConfig::default();

        let site_cfg = SiteScrapeConfig {
            crawl_delay_sec: 123,
            get_from: DateTime::from_str("1984-01-01T12:34:56+00:00").unwrap(),
            get_to: DateTime::from_str("1990-01-01T12:34:56+00:00").unwrap(),
            queue_limit: 0,
        };
        let expected_err = ScrapeConfigValidationError::QueueLimitIsZero;

        let err = site_cfg.validate().unwrap_err().downcast().unwrap();
        assert_eq!(expected_err, err);

        cfg.sites.insert(String::from("some_site"), site_cfg);

        let err = cfg.validate().unwrap_err().downcast().unwrap();
        assert_eq!(expected_err, err);
    }

    #[test]
    fn validate_config_ok() {
        let mut cfg = ScrapeConfig::default();

        let site_cfg = SiteScrapeConfig {
            crawl_delay_sec: 123,
            get_from: DateTime::from_str("1984-01-01T12:34:56+00:00").unwrap(),
            get_to: DateTime::from_str("1990-01-01T12:34:56+00:00").unwrap(),
            queue_limit: 123,
        };

        site_cfg.validate().unwrap();

        cfg.sites.insert(String::from("some_site"), site_cfg);

        cfg.validate().unwrap();
    }
}
