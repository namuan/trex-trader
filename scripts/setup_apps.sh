cd $1 || exit
test -d venv || python3 -m venv venv
venv/bin/pip3 install -r requirements/base.txt
bash ./scripts/start_screen.sh telegram-trex-trader 'venv/bin/python3 telegram-trex-trader.py'