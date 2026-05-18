use serde::Deserialize;
use thiserror::Error;

#[allow(dead_code)]
#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("aboba")]
    BadValue(isize),
}

#[allow(dead_code)]
#[derive(Clone, Debug, Deserialize, Default)]
pub struct PindConfig {
    value: isize,
}

#[allow(dead_code)]
impl PindConfig {
    pub fn validate(&self) -> Result<(), ConfigError> {
        if self.value > 100 {
            Err(ConfigError::BadValue(self.value))
        } else {
            Ok(())
        }
    }
}
