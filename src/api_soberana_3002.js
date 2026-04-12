/**
 * ================================================================
 * HORMIGASAIS · API SOBERANA v1.1 (Puerto 3002 + Dashboard)
 * Orquestador Fénix: Capa de Aplicación LBH
 * Finalidad: Exponer telemetría del enjambre y servir el Dashboard
 * Autor: HormigasAIS-Colonia-Soberana
 * ================================================================
 */

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3002;
const DB_PATH = path.join(__dirname, '../lbh_tiktok.db');
const REPO_DIR = path.join(__dirname, '../evidence');
const DASHBOARD_HTML = path.join(__dirname, 'dashboard.html');

app.use(express.json());

// --- RUTA DEL DASHBOARD VISUAL ---
app.get('/', (req, res) => {
    if (fs.existsSync(DASHBOARD_HTML)) {
        res.sendFile(DASHBOARD_HTML);
    } else {
        res.status(404).send("Error: dashboard.html no encontrado en src/");
    }
});

// Endpoint 1: Estado del Nodo A16
app.get('/api/nodo/status', (req, res) => {
    res.json({
        nodo: "A16-SanMiguel-SV",
        status: "ACTIVE",
        uptime: process.uptime(),
        protocol: "LBH-0006",
        port: PORT
    });
});

// Endpoint 2: Última Evidencia Generada
app.get('/api/evidencia/latest', (req, res) => {
    try {
        const folders = fs.readdirSync(REPO_DIR).filter(f => 
            fs.statSync(path.join(REPO_DIR, f)).isDirectory()
        );
        
        const latestFolder = folders.sort((a, b) => 
            fs.statSync(path.join(REPO_DIR, b)).mtime - fs.statSync(path.join(REPO_DIR, a)).mtime
        )[0];

        if (!latestFolder) return res.status(404).json({ error: "Esperando primera feromona..." });

        const dashboardData = JSON.parse(
            fs.readFileSync(path.join(REPO_DIR, latestFolder, 'dashboard_feed.json'), 'utf8')
        );

        res.json(dashboardData);
    } catch (err) {
        res.status(500).json({ error: "Error leyendo evidencia", details: err.message });
    }
});

// Endpoint 3: Stats de DB
app.get('/api/database/stats', (req, res) => {
    const db = new sqlite3.Database(DB_PATH);
    db.get("SELECT count(*) as count FROM sqlite_master WHERE type='table'", (err, row) => {
        if (err) return res.status(500).json(err);
        res.json({ tables: row.count, db_status: "CONNECTED" });
    });
    db.close();
});

app.listen(PORT, () => {
    console.log(`\n🚀 NODO A16: DASHBOARD ACTIVO`);
    console.log(`🔗 Visualizar en: http://localhost:${PORT}`);
    console.log(`🐜 API Telemetría: http://localhost:${PORT}/api/evidencia/latest\n`);
});
