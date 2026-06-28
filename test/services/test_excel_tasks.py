import sys
from unittest.mock import MagicMock

# Mock out app modules to avoid importing broken packages in the environment
sys.modules["app.models.schema"] = MagicMock()
sys.modules["app.services"] = MagicMock()
sys.modules["app.services.task"] = MagicMock()
sys.modules["app.services.youtube"] = MagicMock()
sys.modules["app.utils"] = MagicMock()

mock_config = MagicMock()
# Return False when getting config properties to bypass youtube limit checks in tests
mock_config.config.youtube.get.return_value = False
sys.modules["app.config"] = mock_config

import unittest
import os
from pathlib import Path
from unittest.mock import patch

# add project root to python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from run_excel_tasks import run_schedule

class TestExcelTasks(unittest.TestCase):
    @patch("run_excel_tasks.load_tasks")
    @patch("run_excel_tasks.save_tasks")
    @patch("run_excel_tasks.execute_task")
    def test_run_schedule_prioritizes_failed_tasks(self, mock_execute, mock_save, mock_load):
        # Setup mock tasks
        # Task 1: pending
        # Task 2: failed
        # Task 3: completed
        # Task 4: failed
        mock_tasks = [
            {"id": "1", "status": "pending", "schedule_time": "", "video_subject": "Subj 1"},
            {"id": "2", "status": "failed", "schedule_time": "", "video_subject": "Subj 2"},
            {"id": "3", "status": "completed", "schedule_time": "", "video_subject": "Subj 3"},
            {"id": "4", "status": "failed", "schedule_time": "", "video_subject": "Subj 4"},
        ]
        mock_load.return_value = mock_tasks
        
        # Track execution order
        executed_ids = []
        def side_effect(row, youtube_schedule=False):
            executed_ids.append(row["id"])
            return "Success"
        
        mock_execute.side_effect = side_effect
        
        # Mock os.path.exists to return True for CSV path
        with patch("os.path.exists", return_value=True):
            run_schedule("dummy.csv", youtube_schedule=False)
            
        # Verify execution order:
        # Failed tasks (2, 4) should be executed first, in their relative original order.
        # Then pending tasks (1) should be executed.
        # Completed tasks (3) should not be executed.
        self.assertEqual(executed_ids, ["2", "4", "1"])
        
        # Verify status updates in mock_tasks:
        # 1, 2, 4 should now be "completed"
        # 3 remains "completed"
        self.assertEqual(mock_tasks[0]["status"], "completed") # id 1
        self.assertEqual(mock_tasks[1]["status"], "completed") # id 2
        self.assertEqual(mock_tasks[2]["status"], "completed") # id 3
        self.assertEqual(mock_tasks[3]["status"], "completed") # id 4

if __name__ == "__main__":
    unittest.main()
