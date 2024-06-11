# import asyncio
# from aiokafka import AIOKafkaProducer

# async def produce_message(broker, topic):
#     producer = AIOKafkaProducer(bootstrap_servers=broker)
#     await producer.start()
#     try:
#         await producer.send_and_wait(topic, b"some_message_bytes")
#     finally:
#         await producer.stop()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(produce_message("localhost:9092", "my_topic"))