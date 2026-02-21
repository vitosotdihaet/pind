use serde::Deserialize;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("aboba")]
    BadValue(isize),
}

#[derive(Clone, Debug, Deserialize, Default)]
pub struct PindConfig {
    value: isize,
}

impl PindConfig {
    pub fn validate(&self) -> Result<(), ConfigError> {
        if self.value > 100 {
            Err(ConfigError::BadValue(self.value))
        } else {
            Ok(())
        }
    }
}
