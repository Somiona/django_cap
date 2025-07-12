# CAP Core - Proof-of-Work Captcha System

A proof-of-work (PoW) based captcha system that requires clients to solve computational challenges to prove they're legitimate users, making it expensive for bots to automate requests.

## How It Works

### 1. Challenge Generation
- Server generates a unique token and creates multiple computational challenges
- Each challenge consists of a **salt** (random hex string) and **target** (difficulty prefix)
- Challenges are deterministically generated using PRNG with the token as seed
- Example challenge: `["e455cea65e98bc3c36287f43769da211", "dceb"]`
  - Salt: `e455cea65e98bc3c36287f43769da211`
  - Target: `dceb` (solution hash must start with this)

### 2. Client Solution Process
- Client receives multiple challenges and must find a nonce for each
- For each challenge, client tries different nonce values until:
  - `SHA256(salt + nonce)` starts with the target prefix
  - This requires computational work proportional to target difficulty

### 3. Solution Validation
- Client submits solutions (array of nonce values)
- Server regenerates the same challenges using the token
- Validates each solution by checking if `SHA256(salt + nonce)` matches target
- If all solutions are valid, server issues a verification token

### 4. Token Usage
- Verification tokens can be used to authenticate requests
- Tokens have configurable expiration times
- Tokens can be consumed (single-use) or preserved for multiple uses

## Key Components

### `Cap` Class
Main orchestrator that handles:
- Challenge creation and storage
- Solution validation
- Token generation and validation

### `DataSource` Interface
Abstraction for persistence layer:
- `store_challenge()` - Save challenge data
- `get_challenge()` - Retrieve challenge by token
- `store_token()` - Save verification tokens
- `validate_token()` - Check token validity
- `cleanup_expired()` - Remove expired data

### Configuration
- `challenge_count`: Number of challenges per captcha
- `challenge_size`: Length of salt (affects memory usage)
- `challenge_difficulty`: Target prefix length (affects CPU time)
- `challenge_expires_ms`: Challenge lifetime
- `token_expires_ms`: Verification token lifetime

## Security Features

- **Deterministic**: Same token always generates same challenges
- **Time-bounded**: Challenges and tokens expire
- **Configurable difficulty**: Adjustable computational cost
- **Token consumption**: Prevents replay attacks
- **Secure randomness**: Uses cryptographically secure random generation

## Use Cases

- API rate limiting
- Form submission protection
- Bot detection and prevention
- Resource-intensive operation gating

## Example Flow

1. Client requests captcha → Server returns token + challenges
2. Client solves challenges → Submits solutions array
3. Server validates solutions → Issues verification token
4. Client uses token for protected operations

This system makes automated attacks expensive while being transparent to legitimate users with modern hardware.
