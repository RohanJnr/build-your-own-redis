from redis.constants import RespFirstByte


class SimpleString:
    @staticmethod
    def construct(value: str) -> str:
        """Construct simple string from a given value."""
        return f"{RespFirstByte.SIMPLE_STRING}{value}\r\n"
