import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from '../types/schema';

// Create a PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Create drizzle database instance
const db = drizzle(pool, { schema });

// Run the migration
async function main() {
  console.log('Starting schema creation...');
  try {
    // Create metrics table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        value NUMERIC NOT NULL,
        unit TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB DEFAULT '{}'::jsonb
      );
    `);

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

    console.log('Schema creation completed successfully');
  } catch (error) {
    console.error('Error creating schema:', error);
    process.exit(1);
  }
  await pool.end();
}

main();