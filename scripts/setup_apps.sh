cd trex-trader-v1 || exit
pip3 install -r requirements/base.txt --user
bash ./scripts/start_screen.sh telegram-trex-trader 'python3 telegram-trex-trader.py'