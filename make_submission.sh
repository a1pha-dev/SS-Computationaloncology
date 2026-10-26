#!/usr/bin/env bash
# Сборка архива для сдачи: ./make_submission.sh <i> <команда>  ->  w<i>_team<команда>.zip
# В архив попадают participants.txt, w<i>/practice.ipynb и, если они есть, w<i>/text/main.pdf (как text.pdf) и таблицы w<i>/*.csv.
set -euo pipefail
cd "$(dirname "$0")"

WEEK="${1:?укажите номер недели и команды, например: ./make_submission.sh 4 04}"
TEAM="${2:?укажите номер команды, например: ./make_submission.sh 4 04}"
DIR="w${WEEK}"
OUT="w${WEEK}_team${TEAM}.zip"

[[ -d "$DIR" ]] || { echo "нет папки $DIR" >&2; exit 1; }
[[ -f "$DIR/practice.ipynb" ]] || { echo "нет $DIR/practice.ipynb" >&2; exit 1; }
if [[ -d "$DIR/text" && ! -f "$DIR/text/main.pdf" ]]; then
    echo "нет $DIR/text/main.pdf — соберите отчёт: cd $DIR/text && latexmk -pdf main.tex" >&2
    exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp participants.txt "$DIR/practice.ipynb" "$TMP/"
shopt -s nullglob
TABLES=("$DIR"/*.csv)
(( ${#TABLES[@]} )) && cp "${TABLES[@]}" "$TMP/"
[[ -f "$DIR/text/main.pdf" ]] && cp "$DIR/text/main.pdf" "$TMP/text.pdf"

rm -f "$OUT"
zip -jq "$OUT" "$TMP"/*
unzip -l "$OUT"
