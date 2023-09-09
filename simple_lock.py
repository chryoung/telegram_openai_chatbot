import uuid
import logging


class Lock:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class LockManager:
    logger = logging.getLogger("lock")

    def __init__(self, redis):
        self.r = redis

    @staticmethod
    def _gpt_lock_key(user_id):
        return F"telegrambot:lock:gpt:{user_id}"

    def lock_gpt(self, user_id, ttl=30):
        lock_key = self._gpt_lock_key(user_id)
        lock_value = str(uuid.uuid4())
        LockManager.logger.info(F"Try to lock gpt service for user id = {user_id}")
        if self.r.set(lock_key, lock_value, nx=True, ex=ttl) == True:
            LockManager.logger.info(F"Locked gpt service for user id = {user_id}, lock_value = {lock_value}")
            return Lock(self._gpt_lock_key(user_id), lock_value)
        else:
            LockManager.logger.warning(F"Failed lock gpt service for user id = {user_id}")
            return None

    def unlock(self, lock: Lock):
        LockManager.logger.info(F"Try to unlock {lock.key}")
        if self.r.get(lock.key) == lock.value:
            self.r.delete(lock.key)
            LockManager.logger.info(F"Unlocked {lock.key} {lock.value}")
            return True
        else:
            LockManager.logger.warning(F"Failed to unlock {lock.key} {lock.value}")
            return False
