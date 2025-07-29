use pyo3::prelude::*;
use sha2::{Digest, Sha256};

/// Generate a pseudorandom string from a seed.
fn _prng(seed: String, length: usize) -> String {
    // FNV-1a hash implementation
    fn fnv1a(s: &str) -> u32 {
        let mut hash: u32 = 2166136261;
        for byte in s.bytes() {
            hash ^= byte as u32;
            hash = hash.wrapping_add(
                (hash << 1)
                    .wrapping_add(hash << 4)
                    .wrapping_add(hash << 7)
                    .wrapping_add(hash << 8)
                    .wrapping_add(hash << 24),
            );
        }
        hash
    }

    let mut state = fnv1a(&seed);
    let mut result = String::new();

    fn next_num(state: u32) -> u32 {
        let mut state = state;
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        state
    }

    while result.len() < length {
        state = next_num(state);
        let rnd = state;
        result.push_str(&format!("{:08x}", rnd));
    }

    result.chars().take(length).collect()
}

fn parse_hex_target(target: &str) -> Vec<u8> {
    // Credit: https://github.com/tiagorangel1/
    let mut padded_target = target.to_string();

    if padded_target.len() % 2 != 0 {
        padded_target.push('0');
    }

    (0..padded_target.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&padded_target[i..i + 2], 16).unwrap())
        .collect()
}

fn write_u64_to_buffer(mut value: u64, buffer: &mut [u8]) -> usize {
    // Credit: https://github.com/tiagorangel1/
    if value == 0 {
        buffer[0] = b'0';
        return 1;
    }

    let mut len = 0;
    let mut temp = value;

    while temp > 0 {
        len += 1;
        temp /= 10;
    }

    for i in (0..len).rev() {
        buffer[i] = (value % 10) as u8 + b'0';
        value /= 10;
    }

    len
}

fn hash_matches_target(hash: &[u8], target_bytes: &[u8], target_bits: usize) -> bool {
    // Credit: https://github.com/tiagorangel1/
    let full_bytes = target_bits / 8;
    let remaining_bits = target_bits % 8;

    if hash[..full_bytes] != target_bytes[..full_bytes] {
        return false;
    }

    if remaining_bits > 0 && full_bytes < target_bytes.len() {
        let mask = 0xFF << (8 - remaining_bits);
        let hash_masked = hash[full_bytes] & mask;
        let target_masked = target_bytes[full_bytes] & mask;
        return hash_masked == target_masked;
    }

    true
}

#[pyfunction]
pub fn rust_prng(seed: String, length: usize) -> PyResult<String> {
    Ok(_prng(seed, length))
}

#[pyfunction]
pub fn rust_generate_challenge_from_token(
    token: String,
    count: usize,
    size: usize,
    difficulty: usize,
) -> PyResult<Vec<(String, String)>> {
    let mut challenges = Vec::new();

    // Placeholder implementation
    for i in 1..(count + 1) {
        let salt = _prng(format!("{}{}", token, i), size);
        let target = _prng(format!("{}{}d", token, i), difficulty);
        challenges.push((salt, target));
    }

    Ok(challenges)
}

#[pyfunction]
pub fn rust_check_answer(challenges: Vec<(String, String)>, solutions: Vec<i64>) -> PyResult<bool> {
    for (idx, (salt, target)) in challenges.iter().enumerate() {
        if idx >= solutions.len() {
            return Ok(false);
        }

        let solution_nonce = solutions[idx] as u64;
        let mut hasher = Sha256::new();
        hasher.update(salt.as_bytes());
        hasher.update(solution_nonce.to_string().as_bytes());
        let hash_result = hasher.finalize();

        let target_bytes = parse_hex_target(target);
        let target_bits = target.len() * 4; // each hex char = 4 bits

        if !hash_matches_target(&hash_result, &target_bytes, target_bits) {
            return Ok(false);
        }
    }
    Ok(true)
}

/// Fast pow solver in Rust.
#[pyfunction]
pub fn rust_solve_pow(salt: String, target: String) -> PyResult<u64> {
    // Credit: https://github.com/tiagorangel1/
    let salt_bytes = salt.as_bytes();

    let target_bytes = parse_hex_target(&target);
    let target_bits = target.len() * 4; // each hex char = 4 bits

    let mut nonce_buffer = [0u8; 20]; // u64::MAX has at most 20 digits

    for nonce in 0..u64::MAX {
        let nonce_len = write_u64_to_buffer(nonce, &mut nonce_buffer);
        let nonce_bytes = &nonce_buffer[..nonce_len];

        let mut hasher = Sha256::new();
        hasher.update(salt_bytes);
        hasher.update(nonce_bytes);
        let hash_result = hasher.finalize();

        if hash_matches_target(&hash_result, &target_bytes, target_bits) {
            return Ok(nonce);
        }
    }

    unreachable!("Solution should be found before exhausting u64::MAX");
}
/// A Python module implemented in Rust.
#[pymodule]
fn _cap_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_prng, m)?)?;
    m.add_function(wrap_pyfunction!(rust_solve_pow, m)?)?;
    m.add_function(wrap_pyfunction!(rust_generate_challenge_from_token, m)?)?;
    m.add_function(wrap_pyfunction!(rust_check_answer, m)?)?;
    Ok(())
}
