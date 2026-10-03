# Response-Format Negotiation

A dependency-free demo of two systems that speak different data formats still understanding each other. They negotiate a shared format, convert between JSON and XML when needed, and fail safely when they can't agree. Pure Python standard library, no external packages, no API keys.

## The flow
NEGOTIATE a common format -> (optionally) CONVERT between JSON and XML -> DELIVER, or FALL BACK safely if no shared format exists.

## Run
`python format_demo.py`
