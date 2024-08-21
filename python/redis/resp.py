from datetime import datetime, timedelta, UTC

from redis.decorators import log_command
from redis.logging import stdout_logger
from redis.formatters import SimpleString, BulkString, RespIntegers


logger = stdout_logger


type ExpireAtTimestamp = float


class Resp:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._expiry: dict[str, ExpireAtTimestamp] = {}

    def ping(self, *args) -> str:
        """

        :param args: list[str]
        :return: str
        """
        return SimpleString.construct("PONG")

    @log_command
    def set(self, *args) -> str:
        """Set key-value pair"""
        key, value = args
        self._data[key] = value
        return SimpleString.construct("OK")

    def get(self, key: str) -> str:
        """Get value for a given key"""
        if key not in self._data:
            return BulkString.NIL
        return BulkString.construct(self._data[key])

    @log_command
    def _expire(self, key: str, timestamp: ExpireAtTimestamp) -> None:
        """Set expiry data for a key given the expiry timestamp."""
        self._expiry[key] = timestamp

    def expire(self, key: str, *args) -> str:
        """
        Set expiry for keys.

        Args:
            key (str): Key name to set expirly

        Returns:
            str: 0 if key not found or 1 if expiry was set
        """
        (seconds,) = args
        if key not in self._data:
            return RespIntegers.construct(0)
        expire_timestamp = (
            datetime.now(UTC) + timedelta(seconds=int(seconds))
        ).timestamp()
        self._expire(key, expire_timestamp)
        return RespIntegers.construct(1)

    def _expire_keys(self) -> None:
        """Expiring keys."""
        current_timestamp = datetime.now().timestamp()
        keys_to_delete = [
            key
            for key, expire_at in self._expiry.items()
            if current_timestamp > expire_at
        ]

        for key in keys_to_delete:
            logger.info(f"Deleting expired key: {key}")
            del self._data[key]
            del self._expiry[key]

    def execute_command(self, command: str, *args) -> str | None:
        """
        Execute a given command.

        Args:
            command (str): Command name (or the first word of a multi-word command)
            args (list[str]): List of arguments passed for that command

        Returns:
            str | None: Response to that command or None if the command does not exist.
        """
        self._expire_keys()
        try:
            logger.opt(ansi=True).info(
                f"Command: <blue>{command}</blue>, Arguments: {args}"
            )
            command_method = getattr(self, command.lower())
            return command_method(*args)
        except Exception as e:
            logger.error(e)
            return None
