#!/bin/zsh
# Whole people pipeline, in order. Each stage reads the previous one's out/ files.
set -e
cd "$(dirname "$0")"
run() { echo "== $1"; perl -e 'alarm shift; exec @ARGV' 900 "${BLENDER:-/usr/local/bin/blender}" -b --python "$1" 2>&1 | grep -E '^\[(pp|face|gm|hair|exp)\]|Error|Traceback|line [0-9]+' ; }
run pp_body.py
run pp_rig.py
run pp_face.py
run pp_garments.py
run pp_hair.py
run pp_lod.py
run export_people.py
