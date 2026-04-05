import unittest
import os
from modules.schema_manager import get_existing_table, compare_schemas, create_table, resolve_schema

class TestSchemaManager(unittest.TestCase):
    def setUp(self):
        self.db = "test_schema.db"  # use a temporary file
        self.table_name = "users"
        self.schema1 = {"name": "TEXT", "age": "INTEGER"}
        self.schema2 = {"name": "TEXT", "age": "INTEGER"}
        self.schema_conflict = {"name": "TEXT", "age": "REAL"}

    def tearDown(self):
        if os.path.exists(self.db):
            os.remove(self.db)
            
    def test_create_table_when_none_exists(self):
        # Table does not exist yet
        action = resolve_schema(self.db, self.table_name, self.schema1)
        self.assertEqual(action, "create")

        # Actually create the table
        create_table(self.db, self.table_name, self.schema1)

        # Verify table exists
        existing = get_existing_table(self.db, self.table_name)
        self.assertIsNotNone(existing)
        self.assertIn("id", existing)      # primary key
        self.assertIn("name", existing)
        self.assertIn("age", existing)

    def test_append_when_schemas_match(self):
        # First, create table
        create_table(self.db, self.table_name, self.schema1)

        # Resolve schema again with matching schema
        action = resolve_schema(self.db, self.table_name, self.schema2)
        self.assertEqual(action, "append")

    def test_conflict_when_schemas_do_not_match(self):
        # First, create table
        create_table(self.db, self.table_name, self.schema1)

        # Resolve schema with conflicting schema
        action = resolve_schema(self.db, self.table_name, self.schema_conflict)
        self.assertEqual(action, "conflict")

    def test_compare_schemas_function(self):
        # No table
        action = compare_schemas(None, {"col1": "TEXT"})
        self.assertEqual(action, "create")
        # Matching schemas
        action = compare_schemas({"col1": "TEXT", "id": "INTEGER"}, {"col1": "TEXT"})
        self.assertEqual(action, "append")
        # Conflict
        action = compare_schemas({"col1": "TEXT"}, {"col1": "REAL"})
        self.assertEqual(action, "conflict")

if __name__ == "__main__":
    unittest.main()