"""
Security middleware for production deployment.
Handles security headers, input validation, and sanitization.
"""

import re
from typing import Any, Dict
from fastapi import Request, HTTPException
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Input validation patterns
AIRPORT_CODE_PATTERN = re.compile(r'^[A-Z]{3}$')
FLIGHT_CODE_PATTERN = re.compile(r'^[A-Z]{2}\d{1,4}$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ISO_DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

# Dangerous characters for SQL/NoSQL injection
DANGEROUS_CHARS = ['<', '>', '"', "'", ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 'script']


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    Production-grade security headers following OWASP recommendations.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Remove server header to prevent fingerprinting
        response.headers.pop('Server', None)
        
        return response


def add_security_headers(response: Response) -> Response:
    """
    Manually add security headers to response.
    Use when SecurityHeadersMiddleware is not applied.
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def validate_airport_code(code: str) -> str:
    """
    Validate and sanitize airport IATA code.
    
    Args:
        code: Airport code to validate
        
    Returns:
        Sanitized uppercase airport code
        
    Raises:
        HTTPException: If code is invalid
    """
    if not code or not isinstance(code, str):
        raise HTTPException(status_code=400, detail="Airport code is required")
    
    code = code.strip().upper()
    
    if not AIRPORT_CODE_PATTERN.match(code):
        raise HTTPException(
            status_code=400,
            detail="Invalid airport code format. Must be 3 uppercase letters (e.g., DXB, LHR, JFK)"
        )
    
    # Check for suspicious patterns
    if any(char in code.lower() for char in DANGEROUS_CHARS):
        logger.warning(f"Suspicious airport code detected: {code}")
        raise HTTPException(status_code=400, detail="Invalid airport code")
    
    return code


def validate_flight_code(code: str) -> str:
    """
    Validate and sanitize flight code.
    
    Args:
        code: Flight code to validate (e.g., EK230, BA123)
        
    Returns:
        Sanitized uppercase flight code
        
    Raises:
        HTTPException: If code is invalid
    """
    if not code or not isinstance(code, str):
        raise HTTPException(status_code=400, detail="Flight code is required")
    
    code = code.strip().upper()
    
    if not FLIGHT_CODE_PATTERN.match(code):
        raise HTTPException(
            status_code=400,
            detail="Invalid flight code format. Must be 2 letters + 1-4 digits (e.g., EK230, BA1234)"
        )
    
    # Check for suspicious patterns
    if any(char in code.lower() for char in DANGEROUS_CHARS):
        logger.warning(f"Suspicious flight code detected: {code}")
        raise HTTPException(status_code=400, detail="Invalid flight code")
    
    return code


def validate_date(date_str: str) -> str:
    """
    Validate date format.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Validated date string
        
    Raises:
        HTTPException: If date format is invalid
    """
    if not date_str or not isinstance(date_str, str):
        raise HTTPException(status_code=400, detail="Date is required")
    
    date_str = date_str.strip()
    
    if not DATE_PATTERN.match(date_str):
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Must be YYYY-MM-DD (e.g., 2024-01-15)"
        )
    
    # Additional validation for reasonable date values
    try:
        year, month, day = map(int, date_str.split('-'))
        if not (1900 <= year <= 2100):
            raise ValueError("Year out of range")
        if not (1 <= month <= 12):
            raise ValueError("Month out of range")
        if not (1 <= day <= 31):
            raise ValueError("Day out of range")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date values: {str(e)}")
    
    return date_str


def validate_iso_datetime(datetime_str: str) -> str:
    """
    Validate ISO datetime format.
    
    Args:
        datetime_str: Datetime string in ISO format
        
    Returns:
        Validated datetime string
        
    Raises:
        HTTPException: If datetime format is invalid
    """
    if not datetime_str or not isinstance(datetime_str, str):
        raise HTTPException(status_code=400, detail="Datetime is required")
    
    datetime_str = datetime_str.strip()
    
    if not ISO_DATETIME_PATTERN.match(datetime_str):
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Must be ISO format (e.g., 2024-01-15T14:30:00)"
        )
    
    return datetime_str


def validate_limit(limit: int, min_val: int = 1, max_val: int = 100) -> int:
    """
    Validate pagination limit parameter.
    
    Args:
        limit: Limit value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated limit value
        
    Raises:
        HTTPException: If limit is out of range
    """
    if not isinstance(limit, int):
        raise HTTPException(status_code=400, detail="Limit must be an integer")
    
    if limit < min_val or limit > max_val:
        raise HTTPException(
            status_code=400,
            detail=f"Limit must be between {min_val} and {max_val}"
        )
    
    return limit


def validate_coordinates(latitude: float, longitude: float) -> tuple:
    """
    Validate geographic coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        Tuple of (latitude, longitude)
        
    Raises:
        HTTPException: If coordinates are invalid
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Coordinates must be valid numbers")
    
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    return (lat, lon)


def sanitize_string_input(value: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent injection attacks.
    
    Args:
        value: String value to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        HTTPException: If input contains dangerous patterns
    """
    if not value or not isinstance(value, str):
        return ""
    
    # Trim whitespace
    value = value.strip()
    
    # Enforce length limit
    if len(value) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input too long. Maximum {max_length} characters allowed"
        )
    
    # Check for dangerous patterns
    value_lower = value.lower()
    for dangerous in DANGEROUS_CHARS:
        if dangerous in value_lower:
            logger.warning(f"Dangerous pattern detected in input: {dangerous}")
            raise HTTPException(
                status_code=400,
                detail="Input contains invalid characters"
            )
    
    return value


def validate_input(data: Dict[str, Any], rules: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate and sanitize input data based on rules.
    
    Args:
        data: Input data dictionary
        rules: Validation rules dictionary
        
    Returns:
        Validated and sanitized data dictionary
        
    Example:
        rules = {
            'airport_code': 'airport',
            'flight_code': 'flight',
            'limit': 'limit'
        }
    """
    validated = {}
    
    for field, rule in rules.items():
        if field not in data:
            continue
            
        value = data[field]
        
        if rule == 'airport':
            validated[field] = validate_airport_code(value)
        elif rule == 'flight':
            validated[field] = validate_flight_code(value)
        elif rule == 'date':
            validated[field] = validate_date(value)
        elif rule == 'datetime':
            validated[field] = validate_iso_datetime(value)
        elif rule == 'limit':
            validated[field] = validate_limit(value)
        elif rule == 'string':
            validated[field] = sanitize_string_input(value)
        else:
            validated[field] = value
    
    return validated
