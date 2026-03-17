"""
Reserved for conversation/memory abstraction.

Per-thread conversation context is currently implemented in the pipeline
(in-memory agent cache keyed by channel_id and thread_ts). This package
is reserved for a future abstraction (e.g. external store for multi-instance).
"""
