# EC2 nginx — mhtran.denniesbor.com
#
# - /api/ and /health|ready  → mhtran-api container on Proxmox VM (via WireGuard VPN)
# - everything else          → GitHub Pages (denniesbor.github.io/mhtran-dash)
#
# Deploy on EC2:
#   sudo cp docker/nginx/mhtran.denniesbor.com /etc/nginx/sites-available/mhtran.denniesbor.com
#   sudo ln -s /etc/nginx/sites-available/mhtran.denniesbor.com /etc/nginx/sites-enabled/
#   sudo nginx -t && sudo systemctl reload nginx
#   sudo certbot --nginx -d mhtran.denniesbor.com
#
# MHTRAN_PORT must match the port exposed by compose.prod.proxmox.yml (default 8036).
# Proxmox VPN IP is 10.8.0.50 — adjust if the lease changes.

server {
    listen 80;
    server_name mhtran.denniesbor.com;

    # API — proxy to the mhtran-api container on Proxmox via VPN
    location /api/ {
        proxy_pass         http://10.8.0.50:8036/api/;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location ~ ^/(health|ready)$ {
        proxy_pass         http://10.8.0.50:8036$request_uri;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
    }

    # Static frontend — proxy to GitHub Pages
    # Requests for /rasters/, /assets/, etc. are forwarded to the Pages CDN.
    location / {
        proxy_pass              https://denniesbor.github.io/mhtran-dash/;
        proxy_ssl_server_name   on;
        proxy_set_header        Host              denniesbor.github.io;
        proxy_set_header        X-Real-IP         $remote_addr;
        proxy_set_header        X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_redirect          off;
    }
}
