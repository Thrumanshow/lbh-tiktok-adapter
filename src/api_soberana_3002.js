const express = require('express');
const { execSync } = require('child_process');
const path = require('path');

const app = express();
const PORT = 3002;
const DB_PATH = path.join(__dirname, '../misiones.db');
const DASHBOARD_HTML = path.join(__dirname, 'dashboard.html');

app.get('/', (req, res) => {
    res.sendFile(DASHBOARD_HTML);
});

app.get('/api/database/stats', (req, res) => {
    try {
        const count = execSync(`sqlite3 ${DB_PATH} "SELECT COUNT(*) FROM misiones;"`).toString().trim();
        res.json({ registros_enjambre: count, db_status: "CONECTADO_A_REYNA" });
    } catch (e) { res.json({ registros_enjambre: 0, db_status: "BUSCANDO..." }); }
});

app.get('/api/evidencia/latest', (req, res) => {
    try {
        // Seleccionamos la fila completa por posición para evitar errores de nombre
        const raw = execSync(`sqlite3 ${DB_PATH} "SELECT * FROM misiones ORDER BY id DESC LIMIT 1;"`).toString().trim();
        const parts = raw.split('|');
        
        // Buscamos el ADN (la cadena más larga que parece hex)
        const adn = parts.find(p => /[0-9a-fA-F]{20,}/.test(p)) || "0xADN_PENDIENTE";
        // El video ID suele ser el segundo o tercer campo
        const videoId = parts.find(p => p.includes('ZSH')) || "ZSHn3d5jY";
        // El score es un número pequeño, usualmente después del ADN
        const score = parts.find(p => !isNaN(p) && p.length <= 3 && p !== parts[0]) || "18";
        const categoria = parts.find(p => ["COLD", "WARM", "HOT", "VIRAL"].includes(p)) || "PROCESANDO";

        res.json({
            video_id: videoId,
            lbh_payload: adn,
            protocolo: `RFC-LBH-0006 | SCORE: ${score} | [${categoria}]`,
            status: "MISIÓN_ACTIVA_OPERANDO"
        });
    } catch (e) { res.status(404).json({ error: "Sincronizando..." }); }
});

app.listen(PORT, () => {
    console.log(`\n✅ NODO A16: MONITOR INTELIGENTE ACTIVADO`);
});
