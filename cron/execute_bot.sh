#!/bin/bash

# PyExecutorHub Bot Execution Script

# Verificar que se proporcione un program_id
if [ -z "$1" ]; then
    echo "Error: Debes proporcionar un program_id"
    echo "Uso: ./execute_bot.sh <program_id> [parameters]"
    echo "Ejemplo: ./execute_bot.sh test_script"
    exit 1
fi

# Configuración
API_URL="http://localhost:8001"
PROGRAM_ID="$1"
PARAMETERS="$2"

# Verificar si la API está disponible
if ! curl -s "$API_URL/health" > /dev/null; then
    echo "Error: API no está disponible en $API_URL"
    exit 1
fi

# Verificar si el programa existe
if ! curl -s "$API_URL/programs" | jq -e ".[] | select(.id == \"$PROGRAM_ID\")" > /dev/null; then
    echo "Error: Programa '$PROGRAM_ID' no encontrado"
    exit 1
fi

# Construir JSON body
if [ -n "$PARAMETERS" ]; then
    JSON_BODY="{\"program_id\": \"$PROGRAM_ID\", \"parameters\": $PARAMETERS}"
else
    JSON_BODY="{\"program_id\": \"$PROGRAM_ID\"}"
fi

# Ejecutar programa
RESPONSE=$(curl -s -X POST "$API_URL/execute" \
    -H "Content-Type: application/json" \
    -d "$JSON_BODY")

# Verificar respuesta
if echo "$RESPONSE" | grep -q "execution_id"; then
    EXECUTION_ID=$(echo "$RESPONSE" | jq -r '.execution_id')
    echo "Ejecución iniciada: $EXECUTION_ID"
    
    # Esperar y mostrar resultado
    sleep 2
    EXECUTION_STATUS=$(curl -s "$API_URL/executions/$EXECUTION_ID")
    STATUS=$(echo "$EXECUTION_STATUS" | jq -r '.status')
    
    if [ "$STATUS" = "completed" ]; then
        echo "Estado: $STATUS"
        echo "$EXECUTION_STATUS" | jq -r '.output' 2>/dev/null
    else
        echo "Estado: $STATUS"
    fi
else
    echo "Error al ejecutar el programa:"
    echo "$RESPONSE" | jq -r '.detail' 2>/dev/null || echo "$RESPONSE"
    exit 1
fi 