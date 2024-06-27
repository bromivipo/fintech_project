import traceback
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import os

async def consume(topic, group, func):
    consumer = AIOKafkaConsumer(
        topic,
        group_id=group,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    try:
        await consumer.start()
        async for message in consumer:
            func(message.value.decode())
    except Exception:
        with open("logs.txt", "a") as file:
            file.write(traceback.format_exc())
    finally:
        await consumer.stop()

async def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_INSTANCE"))
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()