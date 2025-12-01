#!/bin/sh
set -e

SSL_DIR="/etc/nginx/ssl"

if [ ! -f "$SSL_DIR/cert.pem" ] || [ ! -f "$SSL_DIR/key.pem" ]; then
    echo "SSL certificates not found."
    
    mkdir -p "$SSL_DIR"
    
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -days 365 \
        -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost" \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "SSL certificates generated successfully"
        chmod 644 "$SSL_DIR/cert.pem"
        chmod 600 "$SSL_DIR/key.pem"
    else
        echo "Warning: Failed to generate SSL certificates. HTTPS will not work."
    fi
else
    echo "SSL certificates already exist"
fi