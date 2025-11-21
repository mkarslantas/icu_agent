"""
ICU Agent - Multi-Agent System for ICU Patient Monitoring

This package contains the multi-agent system for automated ICU patient
monitoring, analysis, and clinical decision support.
"""

__version__ = "1.0.0"
__author__ = "ICU Agent Team"

from agents.base.agent import BaseAgent
from agents.base.state import StateManager
from agents.base.supervisor import BaseSupervisor

__all__ = [
    "BaseAgent",
    "StateManager",
    "BaseSupervisor",
]
