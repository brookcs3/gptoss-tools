#!/usr/bin/env python3
"""
GPT OSS Enhanced Tmux Session Manager
Automatically manages tmux sessions and long-running processes
"""

import subprocess
import json
import time
import threading
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessInfo:
    """Information about a managed process"""
    pid: int
    name: str
    command: str
    session: str
    window: str
    pane: str
    started_at: datetime
    status: str = "running"  # running, stopped, error
    output_file: Optional[str] = None


@dataclass
class TmuxSession:
    """Tmux session information"""
    name: str
    windows: List[str]
    active: bool
    created_at: datetime
    last_active: datetime


class TmuxManager:
    """Enhanced tmux session manager with process monitoring"""
    
    def __init__(self, base_session: str = "gptoss"):
        self.base_session = base_session
        self.managed_processes: Dict[str, ProcessInfo] = {}
        self.sessions: Dict[str, TmuxSession] = {}
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Session config
        self.config_file = Path(__file__).parent / ".tmux_sessions.json"
        self.logs_dir = Path(__file__).parent / "logs"
        