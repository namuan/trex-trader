#!/usr/bin/env bash
if [[ $# -eq 0 ]] ; then
    echo 'VERSION required as first argument (v<some-number>).'
    echo 'Pls check last version on the server first to avoid overriding'
    echo 'eg. script.sh v6'
    exit 0
fi

VERSION="$1"

sh deploy_all_files.sh $VERSION

# Restart screen sessions
ssh crypto -C "sh start_screen.sh telegram-trex-trader \"cd trextrader_$VERSION; python3.6 telegram-trex-trader.py\""
