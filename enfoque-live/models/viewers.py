from flask import current_app

### Register a user as an active viewer for a stream
def i_am_watching(stream_token: str):
    """
    Marks a user as active for a stream with the given `stream_token`.
    Sets a Redis key with a 10-second TTL to mark the user as active.
    """
    try:
        redis_client = current_app.config['REDIS_CLIENT']
        redis_client.setex(f"active_user:{stream_token}", 10, 'active')
    except:
        print("error to register viewer!")

### Count the number of active users
def count_active_users():
    """
    Counts the number of active users by iterating over Redis keys that match the pattern `active_user:*`.
    Sets a Redis key `total_current_viewers` with the total count.
    """
    redis_client = current_app.config['REDIS_CLIENT']
    total = 0
    for _ in redis_client.scan_iter('active_user*'):
        total += 1
    redis_client.set("total_current_viewers", total)

### Get the total number of current viewers with a lock mechanism
def get_current_viewers():
    """
    Returns the total number of current viewers.
    Uses a lock mechanism to ensure that the count is updated only once every 10 seconds.
    If the lock is not set, it calls `count_active_users()` to update the count.
    """
    try:
        redis_client = current_app.config['REDIS_CLIENT']
        if not redis_client.exists("viewers_count_lock"):
            count_active_users()
            redis_client.setex("viewers_count_lock", 10, 1)

        total_current_viewers = int(redis_client.get("total_current_viewers") or 0)

        return total_current_viewers
    except:
        print("Error to get current viewers")

### Get the total number of current viewers without a lock mechanism
def get_current_viewers_without_lock():
    """
    Returns the total number of current viewers without using the lock mechanism.
    Calls `count_active_users()` to update the count and then returns the total count.
    """
    redis_client = current_app.config['REDIS_CLIENT']
    count_active_users()
    total_current_viewers = int(redis_client.get("total_current_viewers") or 0)
    return total_current_viewers