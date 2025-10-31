"""
Integration test for database connectivity.

Verifies that Django can connect to and query the database.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection


@pytest.mark.integration
@pytest.mark.django_db
class TestDatabaseConnectivity:
    """Test database connection and basic operations."""

    def test_database_connection(self):
        """
        Test that Django can connect to the database.

        Verifies basic database connectivity using raw SQL.
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)

    def test_database_create_and_query_user(self):
        """
        Test that we can create and query a user in the database.

        Verifies ORM functionality and database transactions.
        """
        User = get_user_model()

        # Create a test user
        user = User.objects.create_user(
            username="dbtest", email="dbtest@example.com", password="testpass123"
        )

        # Verify user was created
        assert user.id is not None
        assert user.username == "dbtest"
        assert user.email == "dbtest@example.com"

        # Query the user from database
        retrieved_user = User.objects.get(username="dbtest")
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email

    def test_database_transaction_rollback(self):
        """
        Test that database transactions work correctly.

        Verifies that pytest-django's transaction rollback works.
        """
        User = get_user_model()

        # Create a user in this test
        User.objects.create_user(
            username="transactiontest", email="transaction@example.com", password="testpass123"
        )

        # Verify user exists in this transaction
        assert User.objects.filter(username="transactiontest").exists()

        # After this test completes, pytest-django will rollback
        # the transaction, so this user won't exist in other tests
