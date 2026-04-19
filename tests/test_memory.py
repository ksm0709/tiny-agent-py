import os
import tempfile
import time
from tiny_agent.memory import SessionMemory


def test_get_archived_message():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = SessionMemory(
            session_id="test_session", max_window_messages=1, db_dir=temp_dir
        )
        memory.add_message({"role": "user", "content": "msg1"})
        memory.add_message({"role": "assistant", "content": "msg2"})

        archived = memory.list_archived_messages()
        assert len(archived) == 1
        msg_id = archived[0]["id"]

        msg = memory.get_archived_message(msg_id)
        assert msg["content"] == "msg1"

        msg_none = memory.get_archived_message(999)
        assert msg_none == {}


def test_search_past_sessions():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory1 = SessionMemory(
            session_id="session1", max_window_messages=0, db_dir=temp_dir
        )
        memory1.add_message({"role": "user", "content": "apple banana"})

        memory2 = SessionMemory(
            session_id="session2", max_window_messages=0, db_dir=temp_dir
        )
        memory2.add_message({"role": "user", "content": "apple orange"})

        results = SessionMemory.search_past_sessions("apple", db_dir=temp_dir)
        assert len(results) == 2

        results_banana = SessionMemory.search_past_sessions("banana", db_dir=temp_dir)
        assert len(results_banana) == 1
        assert results_banana[0]["session_id"] == "session1"

        results_invalid = SessionMemory.search_past_sessions(
            "apple", db_dir="/nonexistent/dir"
        )
        assert len(results_invalid) == 0

        with open(os.path.join(temp_dir, "invalid.db"), "w") as f:
            f.write("not a database")
        results_corrupt = SessionMemory.search_past_sessions("apple", db_dir=temp_dir)
        assert len(results_corrupt) == 2


def test_cleanup_old_sessions():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory1 = SessionMemory(
            session_id="session1", max_window_messages=0, db_dir=temp_dir
        )
        memory1.add_message({"role": "user", "content": "msg1"})

        db_path = os.path.join(temp_dir, "session1.db")

        old_time = time.time() - (10 * 86400)
        os.utime(db_path, (old_time, old_time))

        SessionMemory.cleanup_old_sessions(days_old=7, db_dir=temp_dir)

        assert not os.path.exists(db_path)

        with open(os.path.join(temp_dir, "readonly.db"), "w") as f:
            f.write("readonly")
        readonly_path = os.path.join(temp_dir, "readonly.db")
        os.utime(readonly_path, (old_time, old_time))

        os.chmod(temp_dir, 0o555)
        try:
            SessionMemory.cleanup_old_sessions(days_old=7, db_dir=temp_dir)
            assert os.path.exists(readonly_path)
        finally:
            os.chmod(temp_dir, 0o755)
