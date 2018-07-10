#!/bin/bash

find ./clean_midi -type f -name "*.mid" -print0 | while IFS= read -r -d '' file; do
    printf '%s\n' "$file"
    mscore "$file" -o "$file.musicxml"
done
