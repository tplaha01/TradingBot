# backend/app/core/context.py
from ..broker.paper import PaperBroker

# This will be the single shared broker instance for the entire app
broker = PaperBroker()
