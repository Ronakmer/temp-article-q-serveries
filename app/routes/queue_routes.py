from flask import Blueprint, request, jsonify
import pika
import requests
from datetime import datetime
import uuid
import json
from app.rabbitmq import get_rabbitmq_connection
from app.config.logger import LoggerSetup
from app.config.config import RABBITMQ_HOST, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_API_PORT
import time

queue_bp = Blueprint('queue', __name__)

# Create an instance of LoggerSetup
logger_setup = LoggerSetup()

# Use the setup_logger method to get the logger
logger = logger_setup.setup_logger()
RABBITMQ_AUTH = (RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

class QueueRoutes:
    @staticmethod
    @queue_bp.route("/list", methods=["GET"])
    def list_queues():
        try:
            queue_names_param = request.args.get("queue_names", None)
            requested_queue_names = [name.strip() for name in queue_names_param.split(",") if name.strip()] if queue_names_param else []

            # Fetch queues and consumers
            queues_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/queues"
            queues_response = requests.get(queues_url, auth=RABBITMQ_AUTH)
            if queues_response.status_code != 200:
                return jsonify({"error": "Failed to fetch queues"}), queues_response.status_code

            consumers_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/consumers"
            consumers_response = requests.get(consumers_url, auth=RABBITMQ_AUTH)
            if consumers_response.status_code != 200:
                return jsonify({"error": "Failed to fetch workers"}), consumers_response.status_code

            queues = queues_response.json()
            consumers = consumers_response.json()

            print(queues,'queuesx')
            all_existing_queue_names = {queue.get("name") for queue in queues}

            # Find missing queues
            missing_queues = []
            if requested_queue_names:
                missing_queues = [q for q in requested_queue_names if q not in all_existing_queue_names]
            
            if missing_queues:
                return jsonify({
                    "error": "Some queues not found.",
                    "missing_queues": missing_queues
                }), 404



            # First filter the queues if queue_names provided
            filtered_queues = [
                queue for queue in queues
                if not requested_queue_names or queue.get("name") in requested_queue_names
            ]

            # # If queue_names were provided but no match found, fallback to all queues
            # if requested_queue_names and not filtered_queues:
            #     filtered_queues = queues

            queue_details = []
            for queue in filtered_queues:
                queue_name = queue.get("name")

                queue_workers = [
                    {
                        "consumer_tag": consumer.get("consumer_tag"),
                        "channel_details": consumer.get("channel_details"),
                        "connection_details": consumer.get("connection_details", {}),
                        "pid": consumer.get("channel_details", {}).get("peer_port")
                    }
                    for consumer in consumers
                    if consumer.get("queue", {}).get("name") == queue_name
                ]

                queue_info = {
                    "name": queue_name,
                    "messages": queue.get("messages"),
                    "messages_ready": queue.get("messages_ready"),
                    "messages_unacknowledged": queue.get("messages_unacknowledged"),
                    "messages_persistent": queue.get("messages_persistent"),
                    "worker_count": len(queue_workers),
                    "workers": queue_workers,
                    "worker_pids": [w.get("pid") for w in queue_workers],
                    "memory": queue.get("memory"),
                    "state": queue.get("state"),
                    "reductions": queue.get("reductions"),
                    "node": queue.get("node"),
                    "idle_since": queue.get("idle_since"),
                    "durable": queue.get("durable"),
                    "type": queue.get("type"),
                    "arguments": queue.get("arguments"),
                    "vhost": queue.get("vhost"),
                    "exclusive": queue.get("exclusive"),
                    "auto_delete": queue.get("auto_delete"),
                }

                if "message_stats" in queue:
                    queue_info["message_stats"] = queue["message_stats"]

                queue_details.append(queue_info)

            return jsonify({
                "status": "connected",
                "queue_count": len(queue_details),
                "queues": queue_details
            }), 200

        except Exception as e:
            logger.error(f"Error in list_queues: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    @queue_bp.route("/create", methods=["POST"])
    def create_queue():
        try:
            print("Using RABBITMQ credentials:")
            print(f"RABBITMQ_HOST = {RABBITMQ_HOST}")
            print(f"RABBITMQ_USERNAME = {RABBITMQ_USERNAME}")
            print(f"RABBITMQ_PASSWORD = {RABBITMQ_PASSWORD}")
            data = request.json
            queue_name = data.get("queue_name")
            if not queue_name:
                return jsonify({"error": "queue_name is required"}), 400
            
            connection = get_rabbitmq_connection()
            print(connection,"connection")
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            connection.close()
            
            logger.info(f"Queue '{queue_name}' created successfully")
            return jsonify({"message": f"Queue '{queue_name}' created successfully"}), 201
        except Exception as e:
            logger.error(f"Error in create_queue: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    
    
    # @queue_bp.route("/create", methods=["POST"])
    # def create_queue():
    #     connection = None
    #     channel = None
    #     try:
    #         logger.info(f"Creating queue with RabbitMQ host: {RABBITMQ_HOST}")
            
    #         # Validate request body
    #         if not request.is_json:
    #             return jsonify({"error": "Request must be JSON"}), 400
            
    #         data = request.json
    #         if not data:
    #             return jsonify({"error": "Request body is required"}), 400
                
    #         queue_name = data.get("queue_name")
    #         if not queue_name:
    #             return jsonify({"error": "queue_name is required"}), 400
                
    #         logger.info(f"Attempting to create queue: {queue_name}")
            
    #         # First verify RabbitMQ connection
    #         try:
    #             connection = get_rabbitmq_connection()
    #             if not connection:
    #                 error_msg = "Failed to establish RabbitMQ connection - check credentials and server status"
    #                 logger.error(error_msg)
    #                 return jsonify({"error": error_msg}), 500
    #         except Exception as ce:
    #             error_msg = f"Connection error: {str(ce)}"
    #             logger.error(error_msg)
    #             return jsonify({"error": error_msg}), 500
                
    #         channel = None
    #         try:
    #             channel = connection.channel()
    #             logger.info("Successfully created channel")
                
    #             # Check if queue exists
    #             try:
    #                 channel.queue_declare(queue=queue_name, passive=True)
    #                 logger.info(f"Queue '{queue_name}' already exists")
    #                 return jsonify({"error": f"Queue '{queue_name}' already exists"}), 409
    #             except pika.exceptions.ChannelClosedByBroker as e:
    #                 if e.reply_code == 404:  # Queue doesn't exist
    #                     logger.info(f"Queue '{queue_name}' does not exist, creating it")
    #                     # Create a new channel since the previous one was closed
    #                     channel = connection.channel()
                        
    #                     # # First create the dead letter queue
    #                     # dlq_name = f"{queue_name}_dlq"
    #                     # channel.queue_declare(
    #                     #     queue=dlq_name,
    #                     #     durable=True
    #                     # )
                        
    #                     # Create the main queue without dead letter configuration
    #                     channel.queue_declare(
    #                         queue=queue_name, 
    #                         durable=True,  # Queue will survive broker restart
    #                         arguments={
    #                             'x-message-ttl': 1800000,  # 30 minutes in milliseconds
    #                             'x-max-retries': 3  # Custom argument to track retries (optional)
    #                         }
    #                     )
                        
    #                     logger.info(f"Queue '{queue_name}' and its DLQ created successfully")
    #                     return jsonify({
    #                         "message": f"Queue '{queue_name}' created successfully",
    #                         # "dlq_name": dlq_name
    #                     }), 201
    #                 else:
    #                     error_msg = f"Unexpected error code {e.reply_code} when checking queue existence"
    #                     logger.error(error_msg)
    #                     return jsonify({"error": error_msg}), 500
                
    #         except pika.exceptions.AMQPConnectionError as e:
    #             error_msg = f"Failed to connect to RabbitMQ: {str(e)}"
    #             logger.error(error_msg)
    #             return jsonify({"error": error_msg}), 500
                
    #         except pika.exceptions.AMQPChannelError as e:
    #             error_msg = f"Channel error: {str(e)}"
    #             logger.error(error_msg)
    #             return jsonify({"error": error_msg}), 500
                
    #         except Exception as e:
    #             error_msg = f"Unexpected error creating queue: {str(e)}"
    #             logger.error(error_msg)
    #             return jsonify({"error": error_msg}), 500
                
    #     except Exception as e:
    #         error_msg = f"Error in create_queue: {str(e)}"
    #         logger.error(error_msg)
    #         return jsonify({"error": error_msg}), 500
            
    #     finally:
    #         try:
    #             if channel:
    #                 channel.close()
    #             if connection:
    #                 connection.close()
    #         except Exception as e:
    #             logger.warning(f"Error closing connection/channel: {str(e)}")

    @staticmethod
    @queue_bp.route("/delete/<queue_name>", methods=["DELETE"])
    def delete_queue(queue_name):
        try:
	    
            # Define vhost and encode it
            # vhost = "/"  # Your RabbitMQ virtual host
            encoded_vhost = "%2F"  # URL-encoded version of '/'

            # Build URL to list all queues in the vhost
            queues_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/queues/{encoded_vhost}"
            queues_response = requests.get(queues_url, auth=RABBITMQ_AUTH)

            if queues_response.status_code != 200:
                logger.error(f"Failed to fetch queues: {queues_response.text}")
                return jsonify({"error": "Failed to fetch queues"}), queues_response.status_code

            queues = queues_response.json()
            queue_exists = any(queue.get("name") == queue_name for queue in queues)

            if not queue_exists:
                return jsonify({"error": f"Queue '{queue_name}' not found"}), 404

            # Delete the queue
            delete_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/queues/{encoded_vhost}/{queue_name}"
            delete_response = requests.delete(delete_url, auth=RABBITMQ_AUTH)

            logger.info(f"Delete response status: {delete_response.status_code}, content: {delete_response.text}")

            if delete_response.status_code != 204:
                return jsonify({
                    "error": "Failed to delete queue",
                    "details": delete_response.text
                }), delete_response.status_code

            logger.success(f"Queue '{queue_name}' deleted successfully")
            return jsonify({"message": f"Queue '{queue_name}' deleted successfully"}), 200

        except Exception as e:
            logger.exception(f"Error deleting queue {queue_name}")
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    @queue_bp.route("/publish/<queue_name>", methods=["POST"])
    def publish_message(queue_name):
        try:
            data = request.json
            # print(data,'OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
            if not data:
                return jsonify({"error": "Request body is required"}), 400

            message = data.get('message')
            if not message:
                return jsonify({"error": "message is required"}), 400

            # Check if workers are available for the queue
            consumers_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/consumers"
            consumers_response = requests.get(consumers_url, auth=RABBITMQ_AUTH)
            
            if consumers_response.status_code != 200:
                return jsonify({"error": "Failed to fetch workers"}), consumers_response.status_code
            
            consumers = consumers_response.json()
            queue_workers = [consumer for consumer in consumers if consumer.get("queue", {}).get("name") == queue_name]

            if not queue_workers:
                return jsonify({"error": f"No workers available for queue: {queue_name}"}), 404

            # Create message data
            message_data = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'message_id': str(uuid.uuid4())
            }

            # Connect to RabbitMQ
            connection = get_rabbitmq_connection()
            channel = connection.channel()

            try:
                # Declare queue
                channel.queue_declare(queue=queue_name, durable=True)

                # Publish message directly to the specified queue
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message_data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json',
                        timestamp=int(time.time())
                    )
                )

                return jsonify({
                    "message": "Message published successfully",
                    "queue": queue_name,
                    "message_id": message_data['message_id']
                }), 200

            finally:
                try:
                    channel.close()
                    connection.close()
                except Exception as e:
                    logger.error(f"Error closing connections: {str(e)}")

        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            return jsonify({
                "error": str(e),
                "queue": queue_name
            }), 500

    @staticmethod
    @queue_bp.route("/clear/<queue_name>", methods=["POST"])
    def clear_queue(queue_name):
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            queue_info = channel.queue_declare(queue=queue_name, passive=True)
            message_count = queue_info.method.message_count
            
            channel.queue_purge(queue=queue_name)
            connection.close()
            
            logger.info(f"Cleared queue {queue_name}: removed {message_count} messages")
            
            return jsonify({
                "message": "Queue cleared successfully",
                "queue_name": queue_name,
                "messages_removed": message_count
            }), 200
            
        except Exception as e:
            logger.error(f"Error clearing queue {queue_name}: {str(e)}")
            return jsonify({"error": str(e)}), 500

