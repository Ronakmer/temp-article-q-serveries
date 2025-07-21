import pika, os

from app.config.logger import LoggerSetup

from app.config.config import RABBITMQ_USERNAME ,RABBITMQ_PASSWORD ,RABBITMQ_HOST , RABBITMQ_PORT

from dotenv import load_dotenv

load_dotenv()

def get_rabbitmq_connection():
    # Get the current process ID
    pid = os.getpid()
    
    # Log connection attempt
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", 5672))
    print(f"Attempting to connect to RabbitMQ at {host}:{port}")
    
    # Set up credentials
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USERNAME", "guest"), 
        os.getenv("RABBITMQ_PASSWORD", "guest")
    )
      # Set up connection parameters with robust timeout settings
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=120,  
        blocked_connection_timeout=60, 
        socket_timeout=30.0,  
        connection_attempts=5,  
        retry_delay=2.0,
        stack_timeout=60,  
        tcp_options={'TCP_KEEPIDLE': 60,  # Keepalive settings
                    'TCP_KEEPINTVL': 10,
                    'TCP_KEEPCNT': 5},
        client_properties={
            'pid': str(pid),
            'connection_name': f'worker-{pid}',
            'app_id': 'rabbitmq-flask-service',
            'connection_type': 'worker'
        }
    )
    
    # Try to establish connection with retry logic
    max_retries = 3
    retry_delay = 2
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"Connection attempt {attempt + 1} of {max_retries}")
            connection = pika.BlockingConnection(parameters)
            
            print("Successfully established RabbitMQ connection")
            return connection
            
        except pika.exceptions.AMQPConnectionError as e:
            last_error = e
            print(f"""Connection attempt {attempt + 1} failed with AMQPConnectionError:
                Error message: {str(e)}
                Connection details:
                - Host: {host}
                - Port: {port}
                - Username: {os.getenv('RABBITMQ_USERNAME')}
                - Socket timeout: {parameters.socket_timeout}
                - Connection timeout: {parameters.blocked_connection_timeout}
                Error type: {type(e).__name__}""")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                
        except Exception as e:
            last_error = e
            print(f"""Unexpected error on connection attempt {attempt + 1}:
                Error message: {str(e)}
                Error type: {type(e).__name__}
                Connection details:
                - Host: {host}
                - Port: {port}""")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    # If we get here, all retries failed
    print(f"""Failed to connect to RabbitMQ after {max_retries} attempts.
        Last error: {str(last_error)}
        Error type: {type(last_error).__name__}""")
    return None