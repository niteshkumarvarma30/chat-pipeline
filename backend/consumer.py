import pika, os, json, time
from supabase import create_client

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uzjksdoqpsjvjmzybyxt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6amtzZG9xcHNqdmptenlieXh0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTI3MjIwMywiZXhwIjoyMDc2ODQ4MjAzfQ.zaRJoDBW4AlHWYAljpg4c2aoH0oWCHchkG_KyNXLdjs")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "chat_messages")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
QUEUE_NAME = "chat_messages"

def callback(ch, method, properties, body):
    print("\n=== Message Processing Started ===")
    print(f"[>] Delivery Tag: {method.delivery_tag}")
    print(f"[>] Exchange: {method.exchange}")
    print(f"[>] Routing Key: {method.routing_key}")
    print(f"[>] Content Type: {properties.content_type}")
    print(f"[>] Message ID: {properties.message_id}")
    print(f"[>] Timestamp: {properties.timestamp}")
    
    try:
        data = json.loads(body)
        print(f"[>] Message Content: {data}")
        
        print("[*] Storing in Supabase...")
        result = supabase.table(SUPABASE_TABLE).insert(data).execute()
        print(f"[v] Supabase Insert Success: {result}")
        
        print("[*] Acknowledging message...")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[v] Message {properties.message_id} processed and acknowledged")
    except json.JSONDecodeError as e:
        print(f"[!] JSON Decode Error: {str(e)}")
        print(f"[!] Raw message body: {body}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"[!] Processing Error: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    print("=== Message Processing Completed ===\n")

def main():
    print(f"[*] Connecting to RabbitMQ at {RABBITMQ_URL}")
    params = pika.URLParameters(RABBITMQ_URL)
    while True:
        try:
            print("[*] Attempting to establish connection...")
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            print("[*] Connected to RabbitMQ successfully")
            
            print(f"[*] Declaring queue: {QUEUE_NAME}")
            queue_info = channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print(f"[*] Queue '{QUEUE_NAME}' has {queue_info.method.message_count} messages waiting")
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            print("[*] Waiting for messages... To exit press CTRL+C")
            channel.start_consuming()
        except Exception as e:
            print(f"[!] RabbitMQ error: {str(e)}")
            print("[*] Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
