#!/bin/sh

TYPES="normal fire water electric grass ice fighting poison ground flying psychic bug rock ghost dragon dark steel fairy"
for TYPE in $TYPES
do
	curl -o "$TYPE.gif" "https://www.serebii.net/pokedex-bw/type/$TYPE.gif"
done

DMG_CLASSES="physical special other"
for DMG_CLASS in $DMG_CLASSES
do
	curl -o "$DMG_CLASS.png" "https://www.serebii.net/pokedex-bw/type/$DMG_CLASS.png"
done

GIFS=$(ls *.gif)
for GIF in $GIFS
do
	FILENAME="${GIF%.*}"
	convert "$GIF" "$FILENAME.png"
done

PNGS=$(ls *.png)
for PNG in $PNGS
do
	magick $PNG -resize 64x24 $PNG
done

rm *.gif
