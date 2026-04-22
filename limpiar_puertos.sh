#!/bin/bash
# Limpiar puertos antes de arrancar
for PORT in 8080 3002 5005; do
    PID=
    if [ -n "" ]; then
        echo "Liberando puerto  (PID: )"
        kill -9  2>/dev/null
    fi
done
echo "Puertos liberados"
