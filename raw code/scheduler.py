import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from datetime import datetime, time
from algo import main


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../log/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('APScheduler')


def my_task():
    logger.info("Running scheduled trading task...")
    date = datetime.now()

    try:
        main()  # Your main task function
        logger.info(f"Ended running task at {date}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} failed with exception: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} completed successfully.")


# Calculate the time remaining for today to determine the end time
now = datetime.now()
end_of_day = datetime.combine(now.date(), time(23, 59, 59))

# Create a scheduler instance
scheduler = BackgroundScheduler()
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

# Run the task immediately
my_task()

# Schedule the task to run every 4 hours starting after this immediate run
scheduler.add_job(my_task, trigger='interval', seconds=30, start_date=now, end_date=end_of_day)

# Start the scheduler
scheduler.start()

# Keep the script running
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
