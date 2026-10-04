# Privacy by Design & Data Governance Framework

The **Social Media Analytics Framework (SocialPulse)** is engineered under strict **Privacy by Design** principles. It operates on social media feeds and audience telemetry while providing mathematical guarantees against re-identification and unauthorized profiling.

---

## 1. Pseudonymization & Irreversible Salted Hashing

- **Zero Raw PII Storage**: Handles, phone numbers, email addresses, and raw author IDs are never persisted to the primary store or emitted in logs.
- **Salted SHA-256 Hashes**: Every author ID is hashed using a secret environment-level salt before normalization:
  $$\text{user\_hash} = \text{SHA256}(\text{SALT} \,\|\, \text{normalized\_handle})[:16]$$
- **Deterministic Anonymization**: Allows internal correlation of interaction edges (replies, retweets, co-engagement) across the network without compromising individual identity.

---

## 2. Strict $k$-Anonymity Guardrails ($k \ge 20$)

Demographic profiling (age brackets, country/state geography, language preference, and professional interest clusters) is **aggregate-only**:
- **Minimum Cohort Threshold**: No sub-cohort with fewer than $k = 20$ distinct users is ever exposed in API responses or frontend charts.
- **Suppression & Masking**: Any cohort where $N < k$ is automatically masked and merged into a generalized category: `"Protected / Sub-threshold (k < 20)"`.
- **Zero Individual Demographic Records**: Inferred demographic attributes are never attached to individual user records in user-facing endpoints.

---

## 3. Rate-Limiting, Backoff, and Platform Compliance

- **Connector Compliance**: X API v2 and Telegram connectors respect platform rate-limits using exponential backoff with jitter.
- **Public Data Only**: The framework strictly operates on public channels, broadcast streams, and opt-in discussion feeds. Direct messages (DMs) and private channels are fundamentally unsupported.
- **Offline / Mock Default**: The framework ships with a high-fidelity synthetic replay generator that allows demonstrations, testing, and audits without connecting to external networks or handling real user data.

---

## 4. Limitations & Ethical Disclosures

1. **Circadian Timezone Inference**: Posting-hour patterns are probabilistic approximations. Shift work, night owls, and VPN proxies can distort geographic inferences.
2. **Code-Mixed Linguistic Nuance**: Sarcasm and sentiment in Hinglish are classified using high-precision heuristic patterns, but cultural irony can still exhibit ambiguity.
3. **Opt-Out Compliance**: If an entity requests data exclusion, purging by salted hash immediately removes all related thread nodes and associated edge weights.
