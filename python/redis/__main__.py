import asyncio
import argparse

from redis.server import RedisServer

parser = argparse.ArgumentParser()
parser.add_argument("--aof", help="Import redis AOF file")
parser.add_argument("--host", help="Import redis AOF file")
parser.add_argument("--port", help="Import redis AOF file")
args = parser.parse_args()


if __name__ == "__main__":
    asyncio.run(RedisServer(args).run())
