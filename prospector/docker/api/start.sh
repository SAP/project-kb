#! /usr/bin/env sh

python api/routers/nvd_feed_update.py
echo "NVD feed download complete"

python main.py