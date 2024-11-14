from kafka import KafkaConsumer
import json

bootstrap_servers = ['localhost:29092']
# consumer = KafkaConsumer( bootstrap_servers=bootstrap_servers)

topicName = 'etl.public.db_football_player'
# Initialize consumer variable
consumer = KafkaConsumer (topicName , 
                          auto_offset_reset='earliest',
                          group_id='test-2',
                          enable_auto_commit=True,
                          bootstrap_servers = bootstrap_servers)

# Read and print message from consumer
for msg in consumer:
    print(json.loads(msg.value))