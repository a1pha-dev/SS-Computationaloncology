#!/usr/bin/env bash
# Сборка архива для сдачи: ./make_submission.sh <неделя> <команда>
# Пример: ./make_submission.sh 4 04  ->  w4_team04.zip
set -euo pipefail
cd "$(dirname "$0")"

WEEK="${1:?укажите номер недели и команды, например: ./make_submission.sh 4 04}"
TEAM="${2:?укажите номер команды, например: ./make_submission.sh 4 04}"
DIR="w${WEEK}"
OUT="w${WEEK}_team${TEAM}.zip"
[[ -d "$DIR" ]] || { echo "нет папки $DIR" >&2; exit 1; }

# таблица, которая сдаётся на этой неделе
case "$WEEK" in
  3) TABLE="$DIR/dataset.csv" ;;
  4) TABLE="$DIR/analytic_table.csv" ;;
  *) echo "для недели $WEEK не задана сдаваемая таблица — добавьте её в case" >&2; exit 1 ;;
esac

# PDF отчёта: собранный LaTeX-проект недели
for PDF in "$DIR/text/main.pdf" "$DIR/text/text.pdf"; do
  [[ -f "$PDF" ]] && break
done
[[ -f "$PDF" ]] || { echo "не найден PDF отчёта в $DIR" >&2; exit 1; }

# список участников: свой для недели, иначе общий в корне
PARTICIPANTS="$DIR/participants.txt"
[[ -f "$PARTICIPANTS" ]] || PARTICIPANTS="participants.txt"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp "$PARTICIPANTS" "$TMP/participants.txt"
cp "$DIR/practice.ipynb" "$TMP/practice.ipynb"
cp "$PDF" "$TMP/text.pdf"
cp "$TABLE" "$TMP/$(basename "$TABLE")"

rm -f "$OUT"
zip -j "$OUT" "$TMP"/*
unzip -l "$OUT"
