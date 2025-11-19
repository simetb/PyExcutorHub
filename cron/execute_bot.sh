#!/bin/bash

# PyExecutorHub Bot Execution Script

# Verify that a program_id is provided
if [ -z "$1" ]; then
    echo "Error: You must provide a program_id"
    echo "Usage: ./execute_bot.sh <program_id> [parameters]"
    echo "Example: ./execute_bot.sh test_script"
    exit 1
fi

# Configuration
API_URL="http://localhost:8001"
USERNAME="go55xgr6"
PASSWORD="wC5Br9PrkU"
PROGRAM_ID="$1"
PARAMETERS="$2"

# Verify if the API is available
if ! curl -s "$API_URL/health" > /dev/null; then
    echo "Error: API is not available at $API_URL"
    exit 1
fi

# Get authentication token if credentials are provided
TOKEN=""
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    echo "Obtaining authentication token..."
    TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")
    
    if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
        TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
        echo "✅ Authentication token obtained"
    else
        echo "Error: Could not obtain authentication token"
        echo "$TOKEN_RESPONSE" | jq -r '.detail' 2>/dev/null || echo "$TOKEN_RESPONSE"
        exit 1
    fi
fi

# Verify if the program exists
if [ -n "$TOKEN" ]; then
    if ! curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/programs" | jq -e ".[] | select(.id == \"$PROGRAM_ID\")" > /dev/null; then
        echo "Error: Program '$PROGRAM_ID' not found"
        exit 1
    fi
else
    if ! curl -s "$API_URL/programs" | jq -e ".[] | select(.id == \"$PROGRAM_ID\")" > /dev/null; then
        echo "Error: Program '$PROGRAM_ID' not found"
        exit 1
    fi
fi

# Build JSON body
if [ -n "$PARAMETERS" ]; then
    JSON_BODY="{\"program_id\": \"$PROGRAM_ID\", \"parameters\": $PARAMETERS}"
else
    JSON_BODY="{\"program_id\": \"$PROGRAM_ID\"}"
fi

# Build curl command with authentication if token is available
if [ -n "$TOKEN" ]; then
    CURL_CMD="curl -s -X POST \"$API_URL/executions\" \
        -H \"Authorization: Bearer $TOKEN\" \
        -H \"Content-Type: application/json\" \
        -d \"$JSON_BODY\""
else
    CURL_CMD="curl -s -X POST \"$API_URL/execute\" \
        -H \"Content-Type: application/json\" \
        -d \"$JSON_BODY\""
fi

# Execute program
RESPONSE=$(eval $CURL_CMD)

# Verify response
if echo "$RESPONSE" | grep -q "execution_id"; then
    EXECUTION_ID=$(echo "$RESPONSE" | jq -r '.execution_id')
    echo "Execution started: $EXECUTION_ID"
    
    # Wait and show result
    sleep 2
    if [ -n "$TOKEN" ]; then
        EXECUTION_STATUS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/executions/$EXECUTION_ID")
    else
        EXECUTION_STATUS=$(curl -s "$API_URL/executions/$EXECUTION_ID")
    fi
    STATUS=$(echo "$EXECUTION_STATUS" | jq -r '.status')
    
    if [ "$STATUS" = "completed" ]; then
        echo "Status: $STATUS"
        echo "$EXECUTION_STATUS" | jq -r '.output' 2>/dev/null
    else
        echo "Status: $STATUS"
    fi
else
    echo "Error executing program:"
    echo "$RESPONSE" | jq -r '.detail' 2>/dev/null || echo "$RESPONSE"
    exit 1
fi
