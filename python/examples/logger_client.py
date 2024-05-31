import openreality.sdk.log as lg
import random
import time

logger = lg.LoggingClient(name="test",when="m") # iterat log every minute
#logger.start()

start_time = time.time()
last_log_time = 0

while time.time() - start_time < 120:
    # line below is only for demonstration, don't use it in real code
    level = random.randint(0,4)

    """
        write log
        don't execute level= same way as done here, this is demo
        right way to do it is using lg.LoggingClient:
            LoggingLevel.INFO
            LoggingLevel.DEBUG
            LoggingLevel.WARNING
            LoggingLevel.ERROR
            LoggingLevel.CRITICAL
    """
    curr_time = time.time()
    if curr_time - last_log_time > 2:
        print(f"Logging at level {level}")
        logger.log(level=level, msg=f"Hello World @ {curr_time}")
        last_log_time = curr_time 

#logger.stop()
#logger.join()
