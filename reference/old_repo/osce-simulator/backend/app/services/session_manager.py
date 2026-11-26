from __future__ import annotations

import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: float


@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    case_id: Optional[str]
    title: str
    created_at: float
    updated_at: float
    messages: List[ConversationMessage]
    status: str = "active"


class SessionManager:
    def __init__(self, storage_dir: str = "./.osce_data", ttl_seconds: int = 60 * 60 * 24):
        self._sessions: Dict[str, Dict] = {}
        self._conversations: Dict[str, Conversation] = {}
        self._lock = threading.RLock()
        self._ttl = ttl_seconds
        self._storage_dir = storage_dir
        os.makedirs(self._storage_dir, exist_ok=True)
        # Load existing conversations from disk
        self._load_all_conversations()

    # ---- Session API ----
    def create_session(self, user_id: str, case_id: Optional[str] = None) -> str:
        with self._lock:
            session_id = str(uuid.uuid4())
            now = time.time()
            self._sessions[session_id] = {
                "user_id": user_id,
                "case_id": case_id,
                "created_at": now,
                "touched_at": now,
            }
            # create conversation record
            conv = Conversation(
                conversation_id=session_id,
                user_id=user_id,
                case_id=case_id,
                title=f"Session {session_id[:8]}",
                created_at=now,
                updated_at=now,
                messages=[],
            )
            self._conversations[session_id] = conv
            self._persist_conversation(conv)
            return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        with self._lock:
            data = self._sessions.get(session_id)
            if not data:
                return None
            if time.time() - data.get("touched_at", 0) > self._ttl:
                # expired
                self.delete_session(session_id)
                return None
            return data

    def touch_session(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]["touched_at"] = time.time()

    def delete_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            conv = self._conversations.get(session_id)
            if conv:
                conv.status = "archived"
                conv.updated_at = time.time()
                self._persist_conversation(conv)

    # ---- Conversation API ----
    def append_message(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            conv = self._conversations.get(session_id)
            if not conv:
                return
            conv.messages.append(ConversationMessage(role=role, content=content, timestamp=time.time()))
            conv.updated_at = time.time()
            self._persist_conversation(conv)

    def list_conversations(self, user_id: str) -> List[Dict]:
        with self._lock:
            items = [c for c in self._conversations.values() if c.user_id == user_id]
            items.sort(key=lambda c: c.updated_at, reverse=True)
            return [self._public_conv(c) for c in items]

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        with self._lock:
            c = self._conversations.get(conversation_id)
            if not c or c.user_id != user_id:
                return None
            return self._public_conv(c, include_messages=True)

    def rename_conversation(self, conversation_id: str, user_id: str, title: str) -> bool:
        with self._lock:
            c = self._conversations.get(conversation_id)
            if not c or c.user_id != user_id:
                return False
            c.title = title
            c.updated_at = time.time()
            self._persist_conversation(c)
            return True

    def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        with self._lock:
            c = self._conversations.get(conversation_id)
            if not c or c.user_id != user_id:
                return False
            c.status = "archived"
            c.updated_at = time.time()
            self._persist_conversation(c)
            return True

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        with self._lock:
            c = self._conversations.get(conversation_id)
            if not c or c.user_id != user_id:
                return False
            self._conversations.pop(conversation_id, None)
            # remove file snapshot
            path = os.path.join(self._storage_dir, f"{conversation_id}.json")
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass
            return True

    # ---- Persistence (JSON file snapshots) ----
    def _persist_conversation(self, conv: Conversation) -> None:
        path = os.path.join(self._storage_dir, f"{conv.conversation_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._public_conv(conv, include_messages=True), f, ensure_ascii=False, indent=2)

    def _load_all_conversations(self) -> None:
        """Load all conversation snapshots from disk into memory at startup."""
        try:
            for name in os.listdir(self._storage_dir):
                if not name.endswith(".json"):
                    continue
                path = os.path.join(self._storage_dir, name)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                messages_data = data.get("messages", [])
                messages = [ConversationMessage(**m) for m in messages_data]
                conv = Conversation(
                    conversation_id=data.get("conversation_id", os.path.splitext(name)[0]),
                    user_id=data.get("user_id", "unknown"),
                    case_id=data.get("case_id"),
                    title=data.get("title", f"Session {name[:8]}"),
                    created_at=float(data.get("created_at", time.time())),
                    updated_at=float(data.get("updated_at", time.time())),
                    messages=messages,
                    status=data.get("status", "active"),
                )
                self._conversations[conv.conversation_id] = conv
        except Exception:
            # Best-effort loading; don't crash if a file is malformed
            pass

    def _public_conv(self, conv: Conversation, include_messages: bool = False) -> Dict:
        data = {
            "conversation_id": conv.conversation_id,
            "user_id": conv.user_id,
            "case_id": conv.case_id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "status": conv.status,
            "message_count": len(conv.messages),
        }
        if include_messages:
            data["messages"] = [asdict(m) for m in conv.messages]
        return data


