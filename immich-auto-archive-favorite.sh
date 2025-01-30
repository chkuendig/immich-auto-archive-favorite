#!/usr/bin/env sh

args="--api_key $API_KEY --api_url $API_URL"

BASEDIR=$(dirname "$0")
echo $args | xargs python3 -u $BASEDIR/immich-auto-archive-favorite.py