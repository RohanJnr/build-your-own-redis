from redis.exceptions import RespException
from redis.constants import RespFirstByte


class BulkString:

    NIL = "$-1\r\n"

    @staticmethod
    def validate(value: str) -> int:
        """
        Check for a valid bulk string.

        returns bulk string length.
        raise exception if string is not valid.

        """
        if value[0] != RespFirstByte.BULK_STRING or not value[1:].isnumeric():
            raise RespException("Invalid format for a bulk string.")

        return int(value[1:])

    @staticmethod
    def construct(value: str) -> str:
        """Construct simple string from a given value."""
        return f"${len(value)}\r\n{value}\r\n"
