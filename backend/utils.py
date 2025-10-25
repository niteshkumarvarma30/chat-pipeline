import pika
import os
import json
import time

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME = "chat_messages"

def send_to_rabbitmq(payload):
    try:
        # Connect to RabbitMQ
        print(f"[*] Connecting to RabbitMQ at {RABBITMQ_URL}")
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Declare queue (will create if doesn't exist)
        print(f"[*] Declaring/checking queue: {QUEUE_NAME}")
        initial_queue = channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            exclusive=False,
            auto_delete=False
        )
        print(f"[*] Initial queue message count: {initial_queue.method.message_count}")
        
        # Convert payload to JSON string
        message_body = json.dumps(payload)
        print("\n=== Publishing Message ===")
        print(f"[*] Message payload: {message_body}")
        print(f"[*] Queue name: {QUEUE_NAME}")
        
        # Publish with confirm
        channel.confirm_delivery()
        print("[*] Publisher confirms enabled")
        
        # Send message
        properties = pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json',
            message_id=str(time.time()),  # add timestamp as message ID
            timestamp=int(time.time())
        )
        
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message_body,
            properties=properties,
            mandatory=True  # Ensure message is routable
        )
        print("[*] Message published successfully")
        print("=== Publishing Complete ===\n")
        
        # Verify queue state after sending
        final_queue = channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            exclusive=False,
            auto_delete=False,
            passive=True  # Don't create, just check
        )
        print(f"[*] Final queue message count: {final_queue.method.message_count}")
        
        if final_queue.method.message_count > initial_queue.method.message_count:
            print("[√] Message count increased - message queued successfully")
        else:
            print("[!] Warning: Message count did not increase as expected")
            
        # Verify queue count after sending
        verify_queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)
        print(f"[*] Message sent. Queue now has {verify_queue.method.message_count} messages")
            
        # Close connection properly
        try:
            connection.close()
        except Exception as close_error:
            print(f"[!] Warning: Error while closing connection: {close_error}")
            
    except Exception as e:
        print(f"[!] Error sending message to RabbitMQ: {e}")
        print(f"[!] Error type: {type(e)}")
        raise
