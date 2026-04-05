import unittest
from unittest.mock import patch, MagicMock
from modules.llm_interface import build_schema_context, build_prompt, call_llm, generate_sql

class TestLLMInterface(unittest.TestCase):

    def setUp(self):
        # Example schema for testing
        self.schema_dict = {
            "spotify_data": {
                "track_name": "TEXT",
                "track_artist": "TEXT",
                "track_popularity": "INTEGER"
            }
        }
        self.user_query = "Get top 5 songs by Taylor Swift"

    def test_build_schema_context(self):
        schema_str = build_schema_context(self.schema_dict)
        expected_substr = "- spotify_data (track_name (TEXT), track_artist (TEXT), track_popularity (INTEGER))"
        self.assertIn(expected_substr, schema_str)

    def test_build_prompt_includes_query_and_schema(self):
        prompt = build_prompt(self.user_query, self.schema_dict)
        self.assertIn(self.user_query, prompt)
        self.assertIn("spotify_data", prompt)

    @patch("modules.llm_interface.client.chat.completions.create")
    def test_call_llm_success(self, mock_create):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"sql": "SELECT * FROM spotify_data;", "explanation": "Select all tracks."}'
        mock_create.return_value = mock_response

        result = call_llm("dummy prompt")
        self.assertEqual(result["sql"], "SELECT * FROM spotify_data;")
        self.assertEqual(result["explanation"], "Select all tracks.")

    @patch("modules.llm_interface.client.chat.completions.create")
    def test_call_llm_invalid_json(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not JSON"
        mock_create.return_value = mock_response

        result = call_llm("dummy prompt")
        self.assertEqual(result["sql"], "")
        self.assertIn("Failed to parse JSON", result["explanation"])

    @patch("modules.llm_interface.call_llm")
    def test_generate_sql_returns_expected(self, mock_call_llm):
        # Mock call_llm
        mock_call_llm.return_value = {
            "sql": "SELECT * FROM spotify_data;",
            "explanation": "Select all tracks."
        }
        sql, explanation = generate_sql(self.user_query, self.schema_dict)
        self.assertEqual(sql, "SELECT * FROM spotify_data;")
        self.assertEqual(explanation, "Select all tracks.")

if __name__ == "__main__":
    unittest.main()