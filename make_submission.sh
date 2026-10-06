#!/usr/bin/env bash
# Сборка архива для сдачи: ./make_submission.sh 07  ->  w3_team07.zip
set -euo pipefail
cd "$(dirname "$0")"
TEAM="${1:?укажите номер команды, например: ./make_submission.sh 07}"
OUT="w3_team${TEAM}.zip"
cp text/report/main.pdf text.pdf
rm -f "$OUT"
zip -j "$OUT" participants.txt practice.ipynb text.pdf dataset.csv
rm text.pdf
unzip -l "$OUT"
