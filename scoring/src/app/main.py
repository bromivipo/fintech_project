import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import os
import requests
import json
from common.schemas import MsgFromScoring

async def consume_messages():
    consumer = AIOKafkaConsumer(
        os.getenv("TOPIC_SCORING_REQUEST"),
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
        group_id="scoring",
        enable_auto_commit=True
    )
    await consumer.start()
    
    try:
        async for message in consumer:
            with open("logs.txt", "a") as file:
                file.write(f"Received: {message.value.decode()}, topic: {message.topic}, offset: {message.offset}\n")
            headers = {"Content-Type": "application/json"}
            r = requests.get("http://{}/client_agreements".format(os.getenv("PE_PATH")), headers=headers, params={"client_id": json.loads(message.value.decode())["client_id"]})
            if r.status_code != 200:
                raise RuntimeError
            flag = True
            for agr in r.json():
                msg_from_topic = json.loads(message.value.decode())
                if agr["agreement_status"] != "CLOSED" and agr["agreement_id"] != msg_from_topic["agreement_id"]:
                    flag = False
                    break
            producer = AIOKafkaProducer(
                        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
                    )
            msg = MsgFromScoring(name="scoring response",
                agreement_id=msg_from_topic["agreement_id"],
                product_id=msg_from_topic["product_id"],
                client_id=msg_from_topic["client_id"],
                result_status="CLOSED")
            await producer.start()
            if flag:
                msg.result_status = "APPROVED"
            try:
                await producer.send_and_wait(os.getenv("TOPIC_SCORING_RESPONSE"),
                                                json.dumps(msg.dict()).encode("ascii"))
            finally:
                await producer.stop()
    finally:
        await consumer.stop()

if __name__ == '__main__':
    with open("logs.txt", "a") as file:
        file.write(f"started")
    asyncio.run(consume_messages())