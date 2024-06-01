import openreality.sdk.log as lg
import random
import time

logger = lg.LoggingClient(name="test",when="m") # rotating log every 1min

start_time = time.time()
last_log_time = 0

while time.time() - start_time < 120:
    # line below is only for demonstration, don't use it in real code
    level = random.randint(0,4)

    """
        write log
        don't execute level= same way as done here, this is demo
        right way to do it is using default logging module:
            logging.DEBUG
            logging.INFO
            logging.WARNING
            logging.ERROR
            logging.CRITICAL
    """
    curr_time = time.time()
    if curr_time - last_log_time > 2:
        print(f"Logging at level {level}")
        logger.log(
            level=lg.LOGGING_LEVEL[level],
            msg=f"Hello World @ {curr_time}"
        )
        last_log_time = curr_time 
