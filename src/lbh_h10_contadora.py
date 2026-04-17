#!/usr/bin/env python3
import json
import os
import datetime

class HormigaContadora:
    def __init__(self):
        self.base_dir = os.path.expanduser("~/lbh-tiktok-adapter")
        self.libro_mayor = os.path.join(self.base_dir, "contabilidad_soberana.json")
        self.iva_rate = 0.13  # IVA El Salvador

    def auditar_mision(self, video_id):
        # 1. Localizar Evidencia
        path_evidencia = os.path.join(self.base_dir, f"evidence/{video_id}/dashboard_feed.json")
        
        if not os.path.exists(path_evidencia):
            return f"⚠️ H10: No hay evidencia para el video {video_id}"

        with open(path_evidencia, 'r') as f:
            data = json.load(f)

        # 2. Extraer valores financieros
        ingreso_bruto = 0.15 # Valor nominal por análisis LBH
        costo_ops = data["finanzas"]["costo_operativo_usd"]
        utilidad_neta = ingreso_bruto - costo_ops - (ingreso_bruto * self.iva_rate)

        # 3. Generar Registro Contable (Asiento)
        asiento = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_id": video_id,
            "cliente_nodo": data["nodo"],
            "sello_fiscal_lbh": data["sello"],
            "moneda": "USD",
            "detalles": {
                "ingreso_bruto": ingreso_bruto,
                "iva_retenido": round(ingreso_bruto * self.iva_rate, 4),
                "costo_operativo": costo_ops,
                "utilidad_neta": round(utilidad_neta, 4)
            },
            "estado": "FACTURADO_SOPORTE_DIGITAL"
        }

        # 4. Persistencia en Libro Mayor
        with open(self.libro_mayor, 'a') as lm:
            lm.write(json.dumps(asiento) + "\n")

        self.generar_factura_txt(asiento)
        return f"✅ H10: Asiento contable sellado para {video_id}. Utilidad: ${asiento['detalles']['utilidad_neta']}"

    def generar_factura_txt(self, asiento):
        # Crea una carpeta de facturas si no existe
        folder = os.path.join(self.base_dir, "facturas_digitales")
        os.makedirs(folder, exist_ok=True)
        
        filename = f"FACTURA_{asiento['video_id']}.txt"
        with open(os.path.join(folder, filename), 'w') as f:
            f.write(f"--- HORMIGASAIS S.A. DE C.V. (PROYECTO) ---\n")
            f.write(f"NODO EMISOR: {asiento['cliente_nodo']}\n")
            f.write(f"FECHA: {asiento['fecha']}\n")
            f.write(f"ID TRANSACCION: {asiento['sello_fiscal_lbh']}\n")
            f.write(f"------------------------------------------\n")
            f.write(f"SERVICIO: Analisis de Inteligencia LBH\n")
            f.write(f"SUBTOTAL: ${asiento['detalles']['ingreso_bruto']}\n")
            f.write(f"IVA (13%): ${asiento['detalles']['iva_retenido']}\n")
            f.write(f"TOTAL A PAGAR: ${asiento['detalles']['ingreso_bruto']}\n")
            f.write(f"------------------------------------------\n")
            f.write(f"Soberania de Datos Garantizada por LBH-RFC-0006\n")

if __name__ == "__main__":
    # Prueba rapida si se ejecuta solo
    import sys
    if len(sys.argv) > 1:
        h10 = HormigaContadora()
        print(h10.auditar_mision(sys.argv[1]))
