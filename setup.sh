#!/bin/sh

ANDYBOT_HOME=$(pwd)

# cd into pkmn attachments folder so we can dump PNGs there
cd ./attachments/pkmn

# Create any directories that don't already exist
if [ ! -d "./types" ]; then
	mkdir types
fi
if [ ! -d "./damage_classes" ]; then
	mkdir damage_classes
fi
if [ ! -d "./moves" ]; then
	mkdir moves
fi

# Get all type PNGs from Serebii
TYPES="normal fire water electric grass ice fighting poison ground flying psychic bug rock ghost dragon dark steel fairy"
for TYPE in $TYPES
do
	curl -o "$TYPE.gif" "https://www.serebii.net/pokedex-bw/type/$TYPE.gif"
	convert "$TYPE.gif" "$TYPE.png"
	rm "$TYPE.gif"
done

# Get all damage class PNGs from Serebii
DMG_CLASSES="physical special other"
for DMG_CLASS in $DMG_CLASSES
do
	curl -o "$DMG_CLASS.png" "https://www.serebii.net/pokedex-bw/type/$DMG_CLASS.png"
done
DMG_CLASSES="physical special status"

# Rename "other" to "status" to be consistent with PokeAPI
mv "other.png" "status.png"

# Resize all PNGs to be a standard width and height
SEREBII_PNGS="${TYPES} ${DMG_CLASSES}"
for SEREBII_PNG in $SEREBII_PNGS
do
	magick "$SEREBII_PNG.png" -resize 64x24 "$SEREBII_PNG.png"
done

# Stack all combinations of type+damage class and save them
for DMG_CLASS in $DMG_CLASSES
do
	for TYPE in $TYPES
	do
		convert -append "$TYPE.png" "$DMG_CLASS.png" \
			-gravity South \
			-background transparent \
			-alpha on \
			"./moves/$TYPE-$DMG_CLASS.png"
	done
done

# Move all type PNGs into the types dir
for TYPE in $TYPES
do
	mv "$TYPE.png" "./types"
done

# Move all damage class PNGs into the damage classes dir
for DMG_CLASS in $DMG_CLASSES
do
	mv "$DMG_CLASS.png" "./damage_classes"
done

# Come back to top-level of attachments folder
cd ..

#TODO: Download magic_conch_no.mp3 as an attachment
