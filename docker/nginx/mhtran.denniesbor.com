# Proxmox host nginx — exposes the mhtran API at mhtran.denniesbor.com/api/
# Frontend is served by GitHub Pages at the same domain via CNAME.
#
# Deploy:
#   sudo cp docker/nginx/mhtran.denniesbor.com /etc/nginx/sites-available/mhtran.denniesbor.com
#   sudo ln -s /etc/nginx/sites-available/mhtran.denniesbor.com /etc/nginx/sites-enabled/
#   sudo nginx -t && sudo systemctl reload nginx
#   sudo certbot --nginx -d mhtran.denniesbor.com
#
# MHTRAN_PORT in .env must match the port below (default 8036).

server {
    listen 80;
    server_name mhtran.denniesbor.com;

    # API — proxy to the mhtran-api container
    location /api/ {
        proxy_pass         http://127.0.0.1:8036/api/;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location ~ ^/(health|ready)$ {
        proxy_pass         http://127.0.0.1:8036$request_uri;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
    }

    # Everything else is served by GitHub Pages (CNAME handles it).
    # This block should not be reached in normal operation.
    location / {
        return 404;
    }
}
