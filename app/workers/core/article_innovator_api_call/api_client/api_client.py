import requests
import time, os
from app.config.logger import LoggerSetup
from app.config.config import API_BASE_URL, API_EMAIL, API_PASSWORD

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.auth_token = None
        self.token_expiry = None
        self.session = requests.Session()
        
        # Setup logger
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_logger()
        self.logger = self.logger.bind(component="api_client")
        
        # SSL certificate handling
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.cert_path = os.path.join(BASE_DIR, "cert.pem")
        
        # Check if certificate exists and set SSL verification accordingly
        self.ssl_verify = self._setup_ssl_verification()

        # self.cert_path = r"cert.pem"

        # Define API endpoints
        self.endpoints = {
            'auth': {
                'login': '/api/login/'
            },
            'category': {
                'add': '/api/category/add/',
                'get': '/api/categories/',
                'update': '/api/category/update/{slug_id}',
                'delete': '/api/category/delete/{slug_id}'
            },
            'tag': {
                'add': '/api/tag/add/',
                'get': '/api/tags/',
                'update': '/api/tag/update/{slug_id}',
                'delete': '/api/tag/delete/{slug_id}'
            },
            'supportive-prompt': {
                'add': '/api/supportive-prompt/add/',
                'get': '/api/supportive-prompts/',
                'update': '/api/supportive-prompt/update/{slug_id}',
                'delete': '/api/supportive-prompt/delete/{slug_id}'
            },
            'ai-message': {
                'add': '/message-service-api/ai-message/add/',
                'get': '/message-service-api/ai-messages/',
                'update': '/message-service-api/ai-message/update/{slug_id}/',
                'delete': '/message-service-api/ai-message/delete/{slug_id}/'
            },
            'supportive-prompt-variable': {
            #     'add': '/message-service-api/ai-message/add/',
                'get': '/api/supportive-prompt/replace-output-variable/',
                # 'update': '/message-service-api/ai-message/update/{slug_id}/',
                # 'delete': '/message-service-api/ai-message/delete/{slug_id}/'
            },
            'article-type-variable': {
            #     'add': '/message-service-api/ai-message/add/',
                'get': '/api/article-type/replace-output-variable/',
                # 'update': '/message-service-api/ai-message/update/{slug_id}/',
                # 'delete': '/message-service-api/ai-message/delete/{slug_id}/'
            },
            'input-json': {
                # 'add': '/message-service-api/ai-message/add/',
                'get': '/message-service-api/article-input-json/',
                # 'update': '/message-service-api/ai-message/update/{slug_id}/',
                # 'delete': '/message-service-api/ai-message/delete/{slug_id}/'
            },
            'article': {
                # 'add': '/message-service-api/ai-message/add/',
                'update': '/api/article/update/{slug_id}',
                
            },
           
        }
    
    def _setup_ssl_verification(self):
        """Setup SSL verification based on certificate availability and environment"""
        # Check if we're connecting to localhost/development server
        
        is_localhost = any(host in self.base_url.lower() for host in ['localhost', '127.0.0.1', '0.0.0.0'])
        
        if os.path.exists(self.cert_path):
            self.logger.info(f"Using custom certificate: {self.cert_path}")
            return self.cert_path
        elif is_localhost:
            # For local development servers with self-signed certificates
            self.logger.warning("Detected localhost connection - disabling SSL verification for development")
            self.logger.warning("⚠️  SSL verification is disabled - DO NOT use this in production!")
            return False
        else:
            # For production servers, use system's CA bundle
            self.logger.info("Using system's default CA bundle for SSL verification")
            return True

    def login(self):
        """Authenticate with the API and store the token"""
        try:
            self.session.headers.pop('Authorization', None)  # ✅ Clear old token
            print(self.cert_path, '`self.cert_pathssssdfsdfs`')

            login_url = f"{self.base_url}{self.endpoints['auth']['login']}"
            response = self.session.post(
                login_url,
                json={
                    "email": API_EMAIL,
                    "password": API_PASSWORD,
                    "keep_loggedin": True
                },
                verify=self.ssl_verify,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(data, 'dataaaaaaaaaaaaaaa')
                if data.get('success') and data.get('access_token'):
                    self.auth_token = data['access_token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.logger.info("Successfully authenticated with API")
                    return True
                else:
                    self.logger.error(f"Login failed: {data.get('message')}")
                    return False
            else:
                self.logger.error(f"Login HTTP Error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"  Login error: {str(e)}")
            return False

    def is_token_valid(self):
        """Check if a token exists (simple validity check)"""
        return self.auth_token is not None

    def ensure_authenticated(self):
        """Ensure we have a valid authentication token"""
        if not self.is_token_valid():
            return self.login()
        return True

    def make_request(self, method, endpoint, data=None, params=None, max_retries=3, retry_delay=2):
        """Make an authenticated API request with retry logic"""
        if not self.ensure_authenticated():
            return {"success": False, "error": "Authentication failed"}

        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Making {method} request to {endpoint} (Attempt {attempt + 1}/{max_retries})")
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    verify=self.ssl_verify,
                )

                if response.status_code == 401:  # Token expired
                    self.logger.warning("Token expired, attempting to re-authenticate")
                    if self.login():
                        continue
                    return {"success": False, "error": "Authentication failed"}

                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "data": response.json(),
                        "status_code": response.status_code
                    }

                last_error = f"Request failed with status {response.status_code}: {response.text}"
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

            except requests.RequestException as e:
                last_error = str(e)
                self.logger.error(f"Request exception on attempt {attempt + 1}: {last_error}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {last_error}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts. Last error: {last_error}",
            "attempts": max_retries
        }

    def crud(self, service_name, operation, data=None, item_id=None, params=None, **kwargs):
        """
        Generic CRUD operation handler
        :param service_name: Name of the service (e.g., 'wayback_graph')
        :param operation: CRUD operation ('create', 'read', 'update', 'delete')
        :param data: Data for create/update operations
        :param item_id: ID of the item for read/update/delete operations
        :param params: Query parameters for read operation
        :param kwargs: Additional arguments
        :return: API response
        """
        # Map operations to HTTP methods
        operation_map = {
            'create': ('POST', 'add'),
            'read': ('GET', 'get'),
            'update': ('PATCH', 'update'),
            'delete': ('DELETE', 'delete')
        }

        if operation not in operation_map:
            return {"success": False, "error": f"Invalid operation: {operation}"}

        http_method, endpoint_key = operation_map[operation]
        
        # Get the base endpoint
        if service_name not in self.endpoints:
            return {"success": False, "error": f"Service {service_name} not found"}

        endpoint = self.endpoints[service_name].get(endpoint_key)
        if not endpoint:
            return {"success": False, "error": f"Endpoint {endpoint_key} not found for service {service_name}"}

        # Special handling for create operation response to extract slug_id
        if operation == 'create':
            result = self.make_request(http_method, endpoint, data=data, params=params, **kwargs)
            if result.get("success"):
                # Extract slug_id from nested response
                response_data = result.get("data", {})
                if isinstance(response_data, dict) and "data" in response_data:
                    # Update the response data to use the nested data
                    result["data"] = response_data.get("data")
            return result

        # Handle update/delete operations with slug_id
        if operation in ['update', 'delete'] and item_id:
            # Ensure item_id is a string
            item_id = str(item_id)
            # Format the endpoint with the item_id
            print(item_id,'iiiiiiiiiiii')
            try:
                endpoint = endpoint.format(slug_id=item_id)
                print(endpoint,'iiiiiiiiiiii')
            except (KeyError, ValueError) as e:
                return {"success": False, "error": f"Failed to format endpoint with item_id: {str(e)}"}
            self.logger.info(f"Making {operation} request to endpoint: {endpoint}")
        
        # Handle read 
        if operation == 'read':
            result = self.make_request(http_method, endpoint, data=None, params=params, **kwargs)
            if result.get("success"):
                # Extract slug_id from nested response
                response_data = result.get("data", {})
                if isinstance(response_data, dict) and "data" in response_data:
                    # Update the response data to use the nested data
                    result["data"] = response_data.get("data")
            return result

        # Make the request
        return self.make_request(http_method, endpoint, data=data, params=params, **kwargs)

    # Example usage for a new service:
    # def add_new_service(self, data):
    #     return self.crud('new_service', 'create', data=data)
    # 
    # def get_new_service(self, item_id):
    #     return self.crud('new_service', 'read', item_id=item_id)
    # 
    # def update_new_service(self, item_id, data):
    #     return self.crud('new_service', 'update', data=data, item_id=item_id)
    # 
    # def delete_new_service(self, item_id):
    #     return self.crud('new_service', 'delete', item_id=item_id) 