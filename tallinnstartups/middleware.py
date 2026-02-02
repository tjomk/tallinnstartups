import os
import logging
from django.http import StreamingHttpResponse

blacklist = {
    'install.php',
    '.env',
    '.vscode',
    '.git',
    'sftp.json'
}

logger = logging.getLogger('blacklist')


def is_blacklisted(url):
    return any(entry in url for entry in blacklist)


def simple_middleware(get_response):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '5GB.gz')

    def file_iterator(file_path, chunk_size=8192):
        """Generator function to read file in chunks"""
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except FileNotFoundError:
            # If file doesn't exist, the middleware will handle it
            return

    def middleware(request):
        # Check if file exists and get its size
        if not is_blacklisted(request.path):
            return get_response(request)

        # Get client IP and user agent for better logging
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        
        logger.info(
            f"Blacklist access attempt - IP: {client_ip}, "
            f"User-Agent: {user_agent}, "
            f"URL: {request.path}, "
            f"Method: {request.method}"
        )

        try:
            # Create a streaming response
            response = StreamingHttpResponse(
                file_iterator(file_path),
                content_type='application/gzip'
            )
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = str(5218147)
            response['Content-Disposition'] = 'attachment; filename="index.gz"'

            return response

        except FileNotFoundError:
            # If file doesn't exist, proceed with normal request processing
            return get_response(request)

    return middleware
