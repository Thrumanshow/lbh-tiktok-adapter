# 🐜 LBH-TikTok Adapter

Real-time TikTok E-commerce order processing using LBH binary protocol.

## Key metric
JSON original : 150 bytes
LBH pheromone :  16 bytes
Reduction     : 89.3%
## Components

| File | Role |
|---|---|
| `src/lbh_tiktok_transmuter.py` | JSON → 16-byte binary |
| `src/lbh_tiktok_queue.py` | SQLite queue + worker locking |
| `docs/ARCHITECTURE.md` | Full system design |

## Architecture
TikTok Webhook → Transmuter → Queue → Workers → LBH-Net Swarm
## Run

```bash
python3 src/lbh_tiktok_transmuter.py
python3 src/lbh_tiktok_queue.py
Protocol
Built on LBH v1.1
DOI: 10.5281/zenodo.17767205
CLHQ — El Salvador 2026
