from asyncio import StreamWriter, StreamReader

from redis.logging import stdout_logger
from redis.exceptions import RespException
from redis.formatters import BulkString
from redis.resp import Resp

logger = stdout_logger


class ClientHandler:
    """Listen to redis client commands and execute their resp functions."""

    def __init__(self, reader: StreamReader, writer: StreamWriter, resp: Resp) -> None:
        self.reader = reader
        self.writer = writer
        self.resp = resp

    async def listen(self) -> None:
        """Listen for commands and write back command output."""
        while True:
            try:
                command, *args = await self.collect_inc()
            except Exception as e:
                logger.error(e)
                break
            response = self.resp.execute_command(command, *args)
            if response:
                self.writer.write(response.encode())
            else:
                # self.writer.write(b"%1\r\n+key\r\n+value\r\n")
                self.writer.write(b"*0\r\n")
            await self.writer.drain()

        self.writer.close()
        await self.writer.wait_closed()

    async def collect_inc(self) -> list[str]:
        """
        Collect the entire incoming redis client command with all arguments in an incremental manner.

        Raises:
            Exception: raised when client connection closes.
            RespException: raised when command is not an array representation.

        Returns:
            list[str]: list containing the command and all the arguments decoded from the incoming RESP array.
        """
        buffer = await self.reader.readline()
        data = buffer.decode().strip()
        if not data:
            raise Exception("Connection closed.")
        logger.info(f"Readline: {data}end")

        # Resp request always is an array of bulk strings
        # https://redis.io/docs/latest/develop/reference/protocol-spec/#sending-commands-to-a-redis-server

        if data[0] != "*":
            raise RespException("Client command should start with a bulk string")

        array_size = int(data[1:])
        logger.debug(f"Array size: {array_size}")

        array = []

        for _ in range(array_size):
            array.append(await self._get_bulk_string())

        return array

    async def _get_bulk_string(self) -> str:
        """Deocde RESP bulk string."""
        line = (await self.reader.readline()).decode().strip()
        string_size = BulkString.validate(line)

        # Faster than readline ?
        value = (await self.reader.read(string_size + 2)).decode().strip()
        logger.debug(f"Bulk string: {line}-{value}")
        return value

    async def collect_command(self) -> list[str]:
        buffer = await self.reader.read(500)
        data = buffer.decode()
        logger.debug(f"Received command: {data!r}")

        return data.split("\r\n")
