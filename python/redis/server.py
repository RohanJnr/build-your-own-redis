import argparse
from ast import literal_eval
import asyncio
from pathlib import Path

from redis.resp import Resp
from redis.client_handler import ClientHandler
from redis.logging import stdout_logger as logger


class RedisServer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.aof = args.aof
        self.host = args.host or "127.0.0.1"
        self.port = args.port or 6379
        self.resp = Resp()

    def import_data(self) -> None:
        """
        Import data from AOF file if it exists.
        """
        aof_file = Path(self.aof)
        if not aof_file.exists():
            logger.warning("AOF file does not exist, skipping import.")

        lines: list[str] = aof_file.read_text().split("\n")
        for line in lines:
            if not line:
                break
            _, command, args_string_tuple = line.split("|", 2)
            command_args = literal_eval(args_string_tuple)
            self.resp.execute_command(command, *command_args)

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        Handle a single client as a coroutine.

        Args:
            reader (asyncio.StreamReader): stream to read incomming data
            writer (asyncio.StreamWriter): stream to write outgoing data
        """
        logger.info("Accepted client.")
        client = ClientHandler(reader, writer, self.resp)
        await client.listen()

    async def run(self):
        """Run redis server."""
        if self.aof is not None:
            self.import_data()

        # TODO: refactor AOF log init
        logger.add(
            "logging/AOF.log",
            level="INFO",
            filter=lambda record: record["extra"]["loc"] == "aof"
            if "loc" in record["extra"]
            else False,
            format="{time}|{message}",
        )
        server = await asyncio.start_server(self.handle_client, "127.0.0.1", 6379)

        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        logger.info(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()
