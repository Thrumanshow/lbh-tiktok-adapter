const express = require('express');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3002;
const DB_PATH = path.join(__dirname, '../lbh_tiktok.db');
const REPO_DIR = path.join(__dirname, '../evidence');
const DASHBOARD_HTML = path.join(__dirname, 'dashboard.html');

app.get('/', (req, res) => {
    if (fs.existsSync(DASHBOARD_HTML)) {
        res.sendFile(DASHBOARD_HTML);
    } else {
        res.status(404).send("Dashboard HTML no encontrado en src/");
    }
});

app.get('/api/nodo/status', (req, res) => {
    res.json({ 
        nodo: "A16-SanMiguel-SV", 
        status: "ACTIVE", 
        uptime: process.uptime(),
        python_ver: "3.13.13",
        sqlite_ver: "3.53.0"
    });
});

app.get('/api/evidencia/latest', (req, res) => {
    try {
        const folders = fs.readdirSync(REPO_DIR).filter(f => fs.statSync(path.join(REPO_DIR, f)).isDirectory());
        const latest = folders.sort((a, b) => fs.statSync(path.join(REPO_DIR, b)).mtime - fs.statSync(path.join(REPO_DIR, a)).mtime)[0];
        const data = JSON.parse(fs.readFileSync(path.join(REPO_DIR, latest, 'dashboard_feed.json'), 'utf8'));
        res.json(data);
    } catch (err) { res.status(404).json({ error: "Sincronizando con el enjambre..." }); }
});

app.get('/api/database/stats', (req, res) => {
    try {
        // Usando el binario recién instalado en /usr/bin/sqlite3
        const tables = execSync(`sqlite3 ${DB_PATH} "SELECT count(*) FROM sqlite_master WHERE type='table';"`).toString().trim();
        res.json({ tables, db_status: "CONNECTED_VIA_SYSTEM_V3.53" });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

app.listen(PORT, () => {
    console.log(`\n🚀 NODO A16: API SOBERANA v1.2 ACTIVA`);
    console.log(`🔗 Dashboard: http://localhost:${PORT}`);
    console.log(`🐜 Telemetría: http://localhost:${PORT}/api/evidencia/latest\n`);
});
