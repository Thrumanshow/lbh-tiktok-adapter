# Cristhiam Leonardo Hernández Quiñonez
**Solution Architect · LBH Protocol Author · El Salvador 🇸🇻**

📧 chrisquionez354@gmail.com
🔗 linkedin.com/in/cristhiam-lbh-architect
🐙 github.com/HormigasAIS · github.com/Thrumanshow
🌐 thrumanshow.github.io/hormigasais-site/
📄 DOI: 10.5281/zenodo.17767205

---

## Summary

Independent solution architect specializing in distributed systems,
binary protocol design, and real-time e-commerce infrastructure.
Author of the LBH Protocol — a sovereign P2P mesh network built
entirely from Termux on Android in El Salvador.

Designed and implemented a TikTok E-commerce order adapter achieving
89.3% bandwidth reduction (150 bytes JSON → 16 bytes binary),
capable of processing 1B+ events per day.

---

## Technical Skills

**Languages:** Go, Python, JavaScript
**Protocols:** gRPC, REST, TCP/UDP, LBH v1.1
**Databases:** SQLite, PostgreSQL
**Cryptography:** Ed25519, HMAC-SHA256, CRC-16
**Infrastructure:** Docker, Git, Gitea, GitHub Actions
**Concepts:** Distributed Systems, P2P Networks, Binary Protocols,
              Edge Computing, Event-Driven Architecture,
              Concurrent Worker Pipelines, OpenAPI Integration

---

## Projects

### lbh-tiktok-adapter — TikTok E-commerce Protocol Adapter
*2026 · github.com/Thrumanshow/lbh-tiktok-adapter*

Designed and built a binary protocol adapter for TikTok E-commerce
order processing. Transforms JSON order events into 16-byte LBH
pheromones with built-in CRC-16 integrity verification.

- **89.3% bandwidth reduction** (150 bytes → 16 bytes per event)
- At 1B events/day: 139 GB → 14.9 GB saved daily
- Claim-based SQLite locking — zero race conditions across workers
- Retry + exponential backoff + dead-letter queue
- References RFC-LBH-0004 (Data Integrity) + RFC-LBH-0006 (Signal Standard)
- Architecture documented for Salesforce Commerce Cloud, Shopify, Channel Advisor

---

### LBH-Net — Sovereign P2P Swarm Network
*2026 · github.com/HormigasAIS/LBH-Net · v1.5.0*

Designed and built a full P2P mesh network from scratch.
Nodes discover each other automatically via UDP broadcast
without Git, without central registry, without cloud.

- UDP autodiscovery (port 9199) — nodes join the network automatically
- TCP socket server (port 9200) — real-time signal transport
- Ed25519 cryptographic identity per node
- SQLite queue with concurrent worker locking
- Heartbeat + autocure — dead nodes cleaned automatically
- Retry + backoff + dead-letter queue for fault tolerance
- Health check dashboard — http://localhost:8080
- v0.1 → v1.5 in a single development session

---

### lbh-node-service — Go Microservice
*2026 · github.com/HormigasAIS/lbh-node-service · v0.2.0*

Production-grade Go microservice implementing the LBH protocol
with simultaneous REST and gRPC interfaces.

- REST API (Gin, port 8100) + gRPC (port 7100)
- SQLite persistence via GORM
- TCP bridge for CENTINELA_V24 packets (port 9001)
- /metrics telemetry endpoint
- Three live validated nodes: A16-Soberano-Salvador, A20s-AirCity, CENTINELA-V24

---

### HormigasAIS-AirCity — Airport UTM Protocol
*2026 · github.com/HormigasAIS/HormigasAIS-AirCity*

Sovereign drone authorization protocol for airport airspace management.
Target deployment: Aeropuerto del Pacífico, El Salvador, 2027.

- LBH-based signal authorization for drone traffic
- Edge computing architecture for real-time UTM decisions
- Designed for infrastructure with no internet dependency

---

### LBH Protocol — Open Sovereign Protocol
*2025-2026 · github.com/HormigasAIS/HormigasAIS-LBH-Protocol*

Author of the LBH (Lenguaje Binario HormigasAIS) protocol.
RFC-LBH-0001 through RFC-LBH-0006 fully documented.
Published with academic DOI certification.

- DOI: 10.5281/zenodo.17767205
- RFC-LBH-0006: Signal standard with HMAC-SHA256 verification
- RFC-LBH-0004: Data integrity with CRC-16 checksum
- Inspired by ant colony pheromone communication systems

---

### lbh-image-validator — Intellectual Property Validator
*2026 · github.com/HormigasAIS/lbh-image-validator · v0.1.0*

Sovereign digital asset validator using Ed25519 + SHA256.
Generates .identity.lbh, .signature, and .manifest.json
for any PNG file. Includes official Dockerfile.

---

## Protocol Ecosystem

| Repo | Role | Status |
|---|---|---|
| LBH-Net | P2P swarm network | v1.5.0 ✅ |
| lbh-node-service | Go microservice | v0.2.0 ✅ |
| lbh-tiktok-adapter | E-commerce adapter | v1.0 ✅ |
| HormigasAIS-AirCity | Airport UTM | In development |
| LBH-Protocol | RFC specifications | DOI certified ✅ |
| lbh-image-validator | IP validator | v0.1.0 ✅ |

---

## Education & Credentials

- **LBH Protocol** — DOI: 10.5281/zenodo.17767205 (Zenodo, 2026)
- Self-directed architecture — built entirely from Android/Termux
- Languages: Spanish (native), English (professional)

---

*San Miguel, El Salvador · March 2026*
