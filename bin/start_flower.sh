 /serf/serf agent -tag role=flower -join $SERF_1_PORT_7946_TCP_ADDR:$SERF_1_PORT_7946_TCP_PORT & 
 celery flower --app=main.celery