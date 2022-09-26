#! /usr/bin/env sh
set -e

python api/routers/nvd_feed_update.py

echo "NVD feed download complete"

python /app/main.py