"""
Unit tests for the PostgreSQL database connection and operations.
"""
import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

# Verify database connection parameters are available
pytestmark = pytest.mark.skipif(
    not (os.getenv('DATABASE_URL') or 
        (os.getenv('PGDATABASE') and os.getenv('PGUSER') and 
         os.getenv('PGPASSWORD') and os.getenv('PGHOST'))),
    reason="Missing required database environment variables"
)

@pytest.fixture
def db_connection():
    """Create a test database connection"""
    if os.getenv('DATABASE_URL'):
        conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    else:
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', '5432'),
            cursor_factory=RealDictCursor
        )

    # Use a transaction that will be rolled back
    conn.autocommit = False

    # Create test table (will be rolled back)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_metrics (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                value NUMERIC NOT NULL,
                unit TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metric_metadata JSONB DEFAULT '{}'::jsonb
            )
        """)

    yield conn

    # Roll back transaction - no need to clean up
    conn.rollback()
    conn.close()

@pytest.fixture
def sample_metrics_data():
    """Generate sample metrics data for testing"""
    now = datetime.now()
    dates = [(now - timedelta(days=30 * i)).isoformat() for i in range(3)]

    return [
        {"name": "Carbon Emissions", "category": "emissions", "value": 45.0, "unit": "tons CO2e", "timestamp": dates[0]},
        {"name": "Energy Consumption", "category": "energy", "value": 1250.0, "unit": "MWh", "timestamp": dates[0]},
        {"name": "Water Usage", "category": "water", "value": 350.0, "unit": "kiloliters", "timestamp": dates[1]},
        {"name": "Waste Recycled", "category": "waste", "value": 75.0, "unit": "percent", "timestamp": dates[2]},
        {"name": "ESG Score", "category": "social", "value": 80.0, "unit": "score", "timestamp": dates[2]}
    ]

def test_database_connection(db_connection):
    """Test that database connection is working"""
    with db_connection.cursor() as cur:
        cur.execute("SELECT 1 as test")
        result = cur.fetchone()
        assert result['test'] == 1

def test_create_metrics_table(db_connection):
    """Test creating the metrics table"""
    with db_connection.cursor() as cur:
        # Check if table exists after creation
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename = 'test_metrics'
            )
        """)
        result = cur.fetchone()
        assert result[0] is True

def test_insert_and_retrieve_metrics(db_connection, sample_metrics_data):
    """Test inserting and retrieving metrics"""
    # Insert sample metrics
    with db_connection.cursor() as cur:
        for metric in sample_metrics_data:
            cur.execute("""
                INSERT INTO test_metrics (name, category, value, unit, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                metric['name'], 
                metric['category'], 
                metric['value'], 
                metric['unit'], 
                metric['timestamp']
            ))

        # Retrieve inserted metrics
        cur.execute("SELECT * FROM test_metrics ORDER BY timestamp")
        retrieved_metrics = cur.fetchall()

        # Verify count matches
        assert len(retrieved_metrics) == len(sample_metrics_data)

        # Verify content (first record)
        assert retrieved_metrics[0]['name'] == sample_metrics_data[0]['name']
        assert retrieved_metrics[0]['category'] == sample_metrics_data[0]['category']
        assert float(retrieved_metrics[0]['value']) == sample_metrics_data[0]['value']
        assert retrieved_metrics[0]['unit'] == sample_metrics_data[0]['unit']

def test_metrics_query_by_category(db_connection, sample_metrics_data):
    """Test querying metrics by category"""
    # Insert sample metrics
    with db_connection.cursor() as cur:
        for metric in sample_metrics_data:
            cur.execute("""
                INSERT INTO test_metrics (name, category, value, unit, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                metric['name'], 
                metric['category'], 
                metric['value'], 
                metric['unit'], 
                metric['timestamp']
            ))

        # Query by category
        cur.execute("SELECT * FROM test_metrics WHERE category = 'emissions'")
        emissions_metrics = cur.fetchall()

        # Verify emissions metrics
        assert len(emissions_metrics) == 1
        assert emissions_metrics[0]['name'] == "Carbon Emissions"

        # Query by different category
        cur.execute("SELECT * FROM test_metrics WHERE category = 'social'")
        social_metrics = cur.fetchall()

        # Verify social metrics
        assert len(social_metrics) == 1
        assert social_metrics[0]['name'] == "ESG Score"