#!/usr/bin/env bash
# Сборка архива для сдачи: ./make_submission.sh <i> <команда>  ->  w<i>_team<команда>.zip
# В архив попадают participants.txt, w<i>/practice.ipynb, w<i>/text/main.pdf (как text.pdf) и таблица w<i>/*.csv.
set -euo pipefail
cd "$(dirname "$0")"

WEEK="${1:?укажите номер недели и команды, например: ./make_submission.sh 4 04}"
TEAM="${2:?укажите номер команды, например: ./make_submission.sh 4 04}"
DIR="w${WEEK}"
OUT="w${WEEK}_team${TEAM}.zip"

[[ -d "$DIR" ]] || { echo "нет папки $DIR" >&2; exit 1; }
[[ -f "$DIR/practice.ipynb" ]] || { echo "нет $DIR/practice.ipynb" >&2; exit 1; }
[[ -f "$DIR/text/main.pdf" ]] || { echo "нет $DIR/text/main.pdf — соберите отчёт: cd $DIR/text && latexmk -pdf main.tex" >&2; exit 1; }

TABLES=("$DIR"/*.csv)
[[ ${#TABLES[@]} -eq 1 && -f "${TABLES[0]}" ]] || { echo "в $DIR должна быть ровно одна сдаваемая таблица *.csv" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp participants.txt "$DIR/practice.ipynb" "${TABLES[0]}" "$TMP/"
cp "$DIR/text/main.pdf" "$TMP/text.pdf"

rm -f "$OUT"
zip -jq "$OUT" "$TMP"/*
unzip -l "$OUT"
