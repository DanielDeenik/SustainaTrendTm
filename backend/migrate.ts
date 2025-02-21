import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from '../types/schema';
import { logger } from './utils/logger';

// Create a PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
    require: true
  }
});

// Create drizzle database instance
const db = drizzle(pool, { schema });

// Run the migration
async function main() {
  logger.info('Starting database migration...');
  try {
    // Verify database connection
    await pool.query('SELECT 1');
    logger.info('Database connection verified');

    // Create metrics table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        value NUMERIC NOT NULL,
        unit TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metric_metadata JSONB DEFAULT '{}'::jsonb
      );
    `);
    logger.info('Metrics table created or verified');

    // Create reports table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        period_start TIMESTAMP NOT NULL,
        period_end TIMESTAMP NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data JSONB DEFAULT '{}'::jsonb
      );
    `);
    logger.info('Reports table created or verified');

    // Create analyses table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS analyses (
        id SERIAL PRIMARY KEY,
        report_id INTEGER REFERENCES reports(id),
        type TEXT NOT NULL,
        results JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        model_version TEXT NOT NULL
      );
    `);
    logger.info('Analyses table created or verified');

    logger.info('All tables created successfully');
  } catch (error) {
    logger.error('Error during migration:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  logger.error('Migration failed:', error);
  process.exit(1);
});
