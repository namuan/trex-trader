#!/usr/bin/env bash
if [[ $# -eq 0 ]] ; then
    echo 'VERSION required as first argument (v<some-number>).'
    echo 'Pls check last version on the server first to avoid overriding'
    echo 'eg. script.sh v6'
    exit 0
fi

VERSION="$1"
find . -type d -name '__pycache__' | xargs rm -rf
rsync -avzr \
            env.cfg \
            exchanges \
            config \
            bot \
            common \
            requirements.txt \
            telegram-trex-trader.py \
            crypto:./trextrader_$VERSION

# Restart screen sessions
scp start_screen.sh crypto:./