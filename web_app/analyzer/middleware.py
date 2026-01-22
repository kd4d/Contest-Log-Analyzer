# web_app/analyzer/middleware.py
#
# Purpose: Middleware to work around Django test client bugs with file uploads
#
# This middleware manually parses multipart form data if Django's parser failed
# to populate request.FILES. This is a workaround for Django test client issues.

import logging
from django.http.multipartparser import MultiPartParser
from django.core.exceptions import SuspiciousOperation

logger = logging.getLogger(__name__)


class TestClientFileUploadMiddleware:
    """
    Middleware to work around Django test client bugs where request.FILES
    is empty even when files are sent in multipart/form-data requests.
    
    This only activates when:
    1. request.method == 'POST'
    2. request.FILES is empty
    3. Content-Type suggests multipart/form-data
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only process POST requests with empty FILES
        if (request.method == 'POST' and 
            not request.FILES and 
            hasattr(request, 'META')):
            
            content_type = request.META.get('CONTENT_TYPE', '')
            
            # Check if this looks like a multipart request
            if 'multipart/form-data' in content_type.lower():
                # Try to manually parse the multipart data
                try:
                    # Get the raw body - but we can't access it after Django has read it
                    # So we need to check if _body exists (set by test client)
                    if hasattr(request, '_body') and request._body:
                        body = request._body
                    elif hasattr(request, '_stream') and hasattr(request._stream, 'read'):
                        # Try to read from stream if it hasn't been consumed
                        try:
                            body = request._stream.read()
                            request._stream.seek(0)  # Reset for normal processing
                        except:
                            body = None
                    else:
                        body = None
                    
                    if body:
                        # Parse multipart data
                        parser = MultiPartParser(request.META, body, [], encoding='utf-8')
                        parsed_data, parsed_files = parser.parse()
                        
                        # Manually populate request.FILES and request.POST
                        if parsed_files:
                            logger.debug(f"TestClientFileUploadMiddleware: Manually parsed {len(parsed_files)} files")
                            for key, value in parsed_files.items():
                                request.FILES[key] = value
                            for key, value in parsed_data.items():
                                # Don't overwrite existing POST data
                                if key not in request.POST:
                                    request.POST[key] = value
                except Exception as e:
                    # If parsing fails, log but don't break the request
                    logger.debug(f"TestClientFileUploadMiddleware: Failed to parse multipart data: {e}")

        response = self.get_response(request)
        return response
