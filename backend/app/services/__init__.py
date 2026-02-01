# AIService is not imported here to avoid loading diffusers/torch on every request
# (e.g. auth). Use get_ai_service() in complete_api.py which imports ai_service lazily.
__all__ = []
