# Returned Errors

Still under construction - a few can be found in [1]

## Rate limit error

    {
     "error": {
      "errors": [
       {
        "domain": "tracks",
        "reason": "rateLimitExceeded",
        "message": "Rate limit exceeded."
       }
      ],
      "code": 403,
      "message": "Rate limit exceeded."
     }
    }

## Entity quota exceeded

    {
     "error": {
      "errors": [
       {
        "domain": "tracks",
        "reason": "dataTooLarge",
        "message": "Entity quota exceeded"
       }
      ],
      "code": 400,
      "message": "Entity quota exceeded"
     }
    }

## Server error

    {
     "error": {
      "errors": [
       {
        "domain": "tracks",
        "reason": "rateLimitExceeded",
        "message": "Server error."
       }
      ],
      "code": 500,
      "message": "Server error."
     }
    }

## Parsing error

    {
     "error": {
      "errors": [
       {
        "domain": "global",
        "reason": "parseError",
        "message": "Parse Error",
       }
      ],
      "code": 400,
      "message": "Parse Error"
     }
    }

## Missing required value

    {
     "error": {
      "errors": [
       {
        "domain": "tracks",
        "reason": "invalidRequest",
        "message": "Missing collection ID."
       }
      ],
      "code": 400,
      "message": "Missing collection ID."
     }
    }

## Too many objects in a request

    {
     "error": {
      "errors": [
       {
        "domain": "tracks",
        "reason": "invalidRequest",
        "message": "Too many objects in request; the limit is 128."
       }
      ],
      "code": 400,
      "message": "Too many objects in request; the limit is 128."
     }
    }

## References

1. https://developers.google.com/maps/documentation/tracks/concepts

