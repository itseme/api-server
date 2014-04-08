/serf/serf agent -tag role=web -join $SERF_1_PORT_7946_TCP_ADDR:$SERF_1_PORT_7946_TCP_PORT &
python main.py