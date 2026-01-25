use std::sync::LazyLock;

pub static _SCRAPED_DOCUMENTS: LazyLock<prometheus::IntCounterVec> = LazyLock::new(|| {
    prometheus::register_int_counter_vec!(
        "pind_scraper_scraped_documents",
        "Number of scraped documents by domain",
        &["domain"]
    )
    .unwrap()
});
