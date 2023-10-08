# tl-exporter

Prometheus exporter for the TP-Link TL-SG105PE switch (and probably similar switches with the same HTML interface).

## Usage

```bash
docker run \
  --env TL_BASE_URL="http://192.168.1.1"
  --env TL_USERNAME="username" \
  --env TL_PASSWORD="password" \
  --publish 8000:8000 \
  ghcr.io/maxmouchet/tl-exporter:main
```

```bash
curl localhost:8000
# HELP tx_good_packets_total 
# TYPE tx_good_packets_total counter
tx_good_packets_total{mac="...",port="0"} 2.56242457e+08
tx_good_packets_total{mac="...",port="1"} 6.7985699e+07
tx_good_packets_total{mac="...",port="2"} 2.244795e+06
tx_good_packets_total{mac="...",port="3"} 8.6253581e+07
tx_good_packets_total{mac="...",port="4"} 5.6429739e+07
# ...
```

## Settings

See [`tl_exporter/settings.py`](tl_exporter/settings.py).
