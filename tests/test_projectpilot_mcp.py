"""Functional and security demonstrations for the ProjectPilot MCP server."""

import unittest
from unittest.mock import patch

import projectpilot_mcp as app


class ProjectPilotTests(unittest.TestCase):
    """Exercise the public MCP functions and both security demonstrations."""

    def setUp(self) -> None:
        app.tasks.clear()

    def test_mcp_registration(self) -> None:
        tool_names = {tool.name for tool in app.server._tool_manager.list_tools()}
        prompt_names = {
            prompt.name for prompt in app.server._prompt_manager.list_prompts()
        }

        self.assertEqual(tool_names, {"add_task", "list_tasks"})
        self.assertEqual(prompt_names, {"plan_my_day"})

    def test_add_task_success(self) -> None:
        result = app.add_task("  Write report  ", " HIGH ")

        self.assertEqual(result["status"], "success")
        self.assertEqual(app.list_tasks(), [{"title": "Write report", "priority": "high"}])

    def test_invalid_priority(self) -> None:
        result = app.add_task("Write report", "urgent")

        self.assertEqual(result, {
            "status": "error",
            "message": "Priority must be one of: low, medium, high.",
        })

    def test_empty_title(self) -> None:
        result = app.add_task("   ", "low")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Title cannot be empty.")

    def test_input_sanitization_exploit(self) -> None:
        malicious_title = "echo hacked; $(touch /tmp/projectpilot-demo)\x1b"
        result = app.add_task(malicious_title, "low")

        self.assertEqual(result["status"], "error")
        self.assertEqual(
            result["message"],
            "Title cannot contain control characters.",
        )
        self.assertEqual(app.list_tasks(), [])
        print("INPUT SANITIZATION DEMO: command-like input and control characters rejected")

    def test_list_tasks(self) -> None:
        app.add_task("First task", "low")
        app.add_task("Second task", "medium")

        self.assertEqual(len(app.list_tasks()), 2)
        self.assertEqual(app.list_tasks()[1]["title"], "Second task")

    def test_plan_my_day(self) -> None:
        app.add_task("Prepare presentation", "high")

        plan = app.plan_my_day()

        self.assertIn("Prepare presentation", plan)
        self.assertIn("high", plan)

    def test_error_disclosure_exploit(self) -> None:
        internal_details = "SECRET=do-not-share /private/path traceback"
        with patch.object(
            app,
            "_store_task",
            side_effect=RuntimeError(internal_details),
        ):
            result = app.add_task("Controlled failure", "low")

        response_text = str(result)
        self.assertEqual(
            result,
            {
                "status": "error",
                "message": "Unable to add the task right now. Please try again.",
            },
        )
        self.assertNotIn("SECRET", response_text)
        self.assertNotIn("/private/path", response_text)
        self.assertNotIn("traceback", response_text.lower())
        print("ERROR DISCLOSURE DEMO: internal failure returned a generic safe message")

    def test_prompt_error_is_safe(self) -> None:
        with patch.object(
            app,
            "_build_day_plan",
            side_effect=RuntimeError("SECRET=hidden /private/path"),
        ):
            result = app.plan_my_day()

        self.assertEqual(
            result,
            "Unable to create a daily plan right now. Please try again.",
        )


if __name__ == "__main__":
    unittest.main()