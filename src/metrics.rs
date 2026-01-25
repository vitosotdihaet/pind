pub fn collect() -> String {
    let encoder = prometheus::TextEncoder::new();
    let metric_families = prometheus::gather();
    encoder.encode_to_string(&metric_families).unwrap()
}
