# Cristhiam Leonardo Hernández Quiñonez
**Arquitecto de Soluciones · Autor del Protocolo LBH · El Salvador 🇸🇻**

📧 chrisquionez354@gmail.com
🔗 linkedin.com/in/cristhiam-lbh-architect
🐙 github.com/HormigasAIS · github.com/Thrumanshow
🌐 thrumanshow.github.io/hormigasais-site/
📄 DOI: 10.5281/zenodo.17767205

---

## Resumen

Arquitecto de soluciones independiente especializado en sistemas
distribuidos, diseño de protocolos binarios e infraestructura de
comercio electrónico en tiempo real. Autor del Protocolo LBH —
una red mesh P2P soberana construida desde Termux en Android,
El Salvador.

Diseñé e implementé un adaptador de órdenes para TikTok E-commerce
que logra 89.3% de reducción de ancho de banda (150 bytes JSON →
16 bytes binario), capaz de procesar más de 1B eventos por día.

---

## Habilidades Técnicas

**Lenguajes:** Go, Python, JavaScript
**Protocolos:** gRPC, REST, TCP/UDP, LBH v1.1
**Bases de datos:** SQLite, PostgreSQL
**Criptografía:** Ed25519, HMAC-SHA256, CRC-16
**Infraestructura:** Docker, Git, Gitea, GitHub Actions
**Conceptos:** Sistemas Distribuidos, Redes P2P, Protocolos Binarios,
               Edge Computing, Arquitectura Orientada a Eventos,
               Pipelines de Workers Concurrentes, Integración OpenAPI

---

## Proyectos

### lbh-tiktok-adapter — Adaptador de Protocolo TikTok E-commerce
*2026 · github.com/Thrumanshow/lbh-tiktok-adapter*

Diseñé y construí un adaptador de protocolo binario para el
procesamiento de órdenes de TikTok E-commerce. Transforma eventos
JSON en feromonas LBH de 16 bytes con verificación de integridad
CRC-16 integrada.

- **89.3% de reducción de ancho de banda** (150 bytes → 16 bytes)
- A 1B eventos/día: 139 GB → 14.9 GB ahorrados diariamente
- Bloqueo SQLite basado en reclamación — cero condiciones de carrera
- Retry + backoff exponencial + dead-letter queue
- Referencia RFC-LBH-0004 (Integridad de Datos) + RFC-LBH-0006 (Señales)
- Arquitectura documentada para Salesforce Commerce Cloud, Shopify, Channel Advisor

---

### LBH-Net — Red Swarm P2P Soberana
*2026 · github.com/HormigasAIS/LBH-Net · v1.5.0*

Diseñé y construí una red mesh P2P completa desde cero.
Los nodos se descubren automáticamente via broadcast UDP
sin Git, sin registro central, sin nube.

- Autodescubrimiento UDP (puerto 9199) — nodos se unen solos
- Servidor TCP (puerto 9200) — transporte de señales en tiempo real
- Identidad criptográfica Ed25519 por nodo
- Cola SQLite con bloqueo de workers concurrentes
- Heartbeat + autocura — nodos muertos se limpian automáticamente
- Retry + backoff + dead-letter queue para tolerancia a fallos
- Dashboard de health check — http://localhost:8080
- v0.1 → v1.5 en una sola sesión de desarrollo

---

### lbh-node-service — Microservicio Go
*2026 · github.com/HormigasAIS/lbh-node-service · v0.2.0*

Microservicio Go de grado producción que implementa el protocolo
LBH con interfaces REST y gRPC simultáneas.

- REST API (Gin, puerto 8100) + gRPC (puerto 7100)
- Persistencia SQLite via GORM
- Bridge TCP para paquetes CENTINELA_V24 (puerto 9001)
- Endpoint de telemetría /metrics
- Tres nodos validados en vivo: A16-Soberano-Salvador, A20s-AirCity, CENTINELA-V24

---

### HormigasAIS-AirCity — Protocolo UTM Aeroportuario
*2026 · github.com/HormigasAIS/HormigasAIS-AirCity*

Protocolo soberano de autorización de drones para gestión
del espacio aéreo aeroportuario. Despliegue objetivo:
Aeropuerto del Pacífico, El Salvador, 2027.

- Autorización de señales LBH para tráfico de drones
- Arquitectura edge computing para decisiones UTM en tiempo real
- Diseñado para infraestructura sin dependencia de internet

---

### Protocolo LBH — Protocolo Soberano Abierto
*2025-2026 · github.com/HormigasAIS/HormigasAIS-LBH-Protocol*

Autor del protocolo LBH (Lenguaje Binario HormigasAIS).
RFC-LBH-0001 al RFC-LBH-0006 completamente documentados.
Publicado con certificación DOI académico.

- DOI: 10.5281/zenodo.17767205
- RFC-LBH-0006: Estándar de señales con verificación HMAC-SHA256
- RFC-LBH-0004: Integridad de datos con checksum CRC-16
- Inspirado en sistemas de comunicación de feromonas de colonias de hormigas

---

### lbh-image-validator — Validador de Propiedad Intelectual
*2026 · github.com/HormigasAIS/lbh-image-validator · v0.1.0*

Validador soberano de activos digitales usando Ed25519 + SHA256.
Genera .identity.lbh, .signature y .manifest.json para archivos PNG.
Incluye Dockerfile oficial.

---

## Ecosistema de Protocolos

| Repositorio | Rol | Estado |
|---|---|---|
| LBH-Net | Red swarm P2P | v1.5.0 ✅ |
| lbh-node-service | Microservicio Go | v0.2.0 ✅ |
| lbh-tiktok-adapter | Adaptador e-commerce | v1.0 ✅ |
| HormigasAIS-AirCity | UTM aeroportuario | En desarrollo |
| LBH-Protocol | Especificaciones RFC | DOI certificado ✅ |
| lbh-image-validator | Validador PI | v0.1.0 ✅ |

---

## Formación y Credenciales

- **Protocolo LBH** — DOI: 10.5281/zenodo.17767205 (Zenodo, 2026)
- Arquitectura autodidacta — construida desde Android/Termux
- Idiomas: Español (nativo), Inglés (profesional)

---

*San Miguel, El Salvador · Marzo 2026*
