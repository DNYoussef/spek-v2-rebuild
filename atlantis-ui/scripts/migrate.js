#!/usr/bin/env node

/**
 * SPEK Platform v2 - Database Migration Runner
 * Week 25 - Desktop Deployment
 *
 * This script manages database migrations for the SPEK platform.
 *
 * Usage:
 *   node scripts/migrate.js up              # Run all pending migrations
 *   node scripts/migrate.js down            # Rollback last migration
 *   node scripts/migrate.js down --all      # Rollback all migrations
 *   node scripts/migrate.js status          # Show migration status
 *   node scripts/migrate.js create <name>   # Create new migration template
 */

const fs = require('fs');
const path = require('path');
const { Client } = require('pg');
require('dotenv').config();

// ============================================
// CONFIGURATION
// ============================================

const MIGRATIONS_DIR = path.join(__dirname, '..', 'prisma', 'migrations');
const ROLLBACK_DIR = path.join(MIGRATIONS_DIR, 'rollback');

const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
    console.error('❌ ERROR: DATABASE_URL environment variable not set');
    console.error('   Please create a .env file with DATABASE_URL');
    process.exit(1);
}

// ============================================
// DATABASE CONNECTION
// ============================================

async function getClient() {
    const client = new Client({
        connectionString: DATABASE_URL,
    });

    await client.connect();
    return client;
}

// ============================================
// MIGRATION TRACKING TABLE
// ============================================

async function ensureMigrationsTable(client) {
    await client.query(`
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    `);
}

async function getAppliedMigrations(client) {
    const result = await client.query(
        'SELECT name FROM _migrations ORDER BY id ASC'
    );
    return result.rows.map(row => row.name);
}

async function recordMigration(client, name) {
    await client.query(
        'INSERT INTO _migrations (name) VALUES ($1)',
        [name]
    );
}

async function removeMigrationRecord(client, name) {
    await client.query(
        'DELETE FROM _migrations WHERE name = $1',
        [name]
    );
}

// ============================================
// MIGRATION DISCOVERY
// ============================================

function getAvailableMigrations() {
    const files = fs.readdirSync(MIGRATIONS_DIR);
    return files
        .filter(file => file.endsWith('.sql') && !file.includes('rollback'))
        .sort();
}

function getRollbackScript(migrationName) {
    const rollbackName = migrationName.replace('.sql', '_rollback.sql');
    const rollbackPath = path.join(ROLLBACK_DIR, rollbackName);

    // Try multiple naming patterns
    const patterns = [
        rollbackName,
        migrationName.replace('.sql', '_rollback.sql'),
        migrationName.split('_')[0] + '_rollback.sql'
    ];

    for (const pattern of patterns) {
        const fullPath = path.join(ROLLBACK_DIR, pattern);
        if (fs.existsSync(fullPath)) {
            return fullPath;
        }
    }

    return null;
}

// ============================================
// COMMAND: UP (Apply migrations)
// ============================================

async function migrateUp() {
    const client = await getClient();

    try {
        console.log('🔄 Running database migrations...\n');

        await ensureMigrationsTable(client);

        const applied = await getAppliedMigrations(client);
        const available = getAvailableMigrations();

        const pending = available.filter(m => !applied.includes(m));

        if (pending.length === 0) {
            console.log('✅ No pending migrations');
            return;
        }

        console.log(`📦 Found ${pending.length} pending migration(s):\n`);

        for (const migration of pending) {
            const migrationPath = path.join(MIGRATIONS_DIR, migration);
            const sql = fs.readFileSync(migrationPath, 'utf8');

            console.log(`   ⏳ Applying: ${migration}`);

            try {
                await client.query('BEGIN');
                await client.query(sql);
                await recordMigration(client, migration);
                await client.query('COMMIT');

                console.log(`   ✅ Applied: ${migration}\n`);
            } catch (error) {
                await client.query('ROLLBACK');
                console.error(`   ❌ Failed: ${migration}`);
                console.error(`   Error: ${error.message}\n`);
                throw error;
            }
        }

        console.log('✅ All migrations applied successfully');
    } catch (error) {
        console.error('\n❌ Migration failed:', error.message);
        process.exit(1);
    } finally {
        await client.end();
    }
}

// ============================================
// COMMAND: DOWN (Rollback migrations)
// ============================================

async function migrateDown(options = {}) {
    const client = await getClient();

    try {
        console.log('🔄 Rolling back migrations...\n');

        await ensureMigrationsTable(client);

        const applied = await getAppliedMigrations(client);

        if (applied.length === 0) {
            console.log('✅ No migrations to rollback');
            return;
        }

        const toRollback = options.all
            ? applied.reverse()
            : [applied[applied.length - 1]];

        console.log(`📦 Rolling back ${toRollback.length} migration(s):\n`);

        for (const migration of toRollback) {
            const rollbackPath = getRollbackScript(migration);

            if (!rollbackPath) {
                console.error(`   ❌ Rollback script not found for: ${migration}`);
                console.error(`   Expected: ${ROLLBACK_DIR}/${migration.replace('.sql', '_rollback.sql')}`);
                continue;
            }

            const sql = fs.readFileSync(rollbackPath, 'utf8');

            console.log(`   ⏳ Rolling back: ${migration}`);

            try {
                await client.query('BEGIN');
                await client.query(sql);
                await removeMigrationRecord(client, migration);
                await client.query('COMMIT');

                console.log(`   ✅ Rolled back: ${migration}\n`);
            } catch (error) {
                await client.query('ROLLBACK');
                console.error(`   ❌ Rollback failed: ${migration}`);
                console.error(`   Error: ${error.message}\n`);
                throw error;
            }
        }

        console.log('✅ Rollback completed successfully');
    } catch (error) {
        console.error('\n❌ Rollback failed:', error.message);
        process.exit(1);
    } finally {
        await client.end();
    }
}

// ============================================
// COMMAND: STATUS (Show migration status)
// ============================================

async function showStatus() {
    const client = await getClient();

    try {
        console.log('📊 Migration Status\n');
        console.log('==================\n');

        await ensureMigrationsTable(client);

        const applied = await getAppliedMigrations(client);
        const available = getAvailableMigrations();

        console.log(`Database: ${DATABASE_URL.split('@')[1]}\n`);
        console.log(`Applied Migrations: ${applied.length}`);
        console.log(`Available Migrations: ${available.length}`);
        console.log(`Pending Migrations: ${available.length - applied.length}\n`);

        if (available.length > 0) {
            console.log('Migration List:');
            console.log('---------------\n');

            for (const migration of available) {
                const isApplied = applied.includes(migration);
                const status = isApplied ? '✅' : '⏳';
                const timestamp = isApplied
                    ? await getMigrationTimestamp(client, migration)
                    : '';

                console.log(`${status} ${migration} ${timestamp}`);
            }
        } else {
            console.log('No migrations found');
        }

        console.log('');
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    } finally {
        await client.end();
    }
}

async function getMigrationTimestamp(client, name) {
    const result = await client.query(
        'SELECT applied_at FROM _migrations WHERE name = $1',
        [name]
    );

    if (result.rows.length > 0) {
        const date = new Date(result.rows[0].applied_at);
        return `(${date.toISOString()})`;
    }

    return '';
}

// ============================================
// COMMAND: CREATE (Create new migration template)
// ============================================

function createMigration(name) {
    if (!name) {
        console.error('❌ ERROR: Migration name required');
        console.error('   Usage: node scripts/migrate.js create <name>');
        process.exit(1);
    }

    const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const filename = `${timestamp}_${name.replace(/\s+/g, '_')}.sql`;
    const rollbackFilename = `${timestamp}_${name.replace(/\s+/g, '_')}_rollback.sql`;

    const migrationPath = path.join(MIGRATIONS_DIR, filename);
    const rollbackPath = path.join(ROLLBACK_DIR, rollbackFilename);

    const template = `-- SPEK Platform v2 - ${name}
-- Migration: ${filename}
-- Created: ${new Date().toISOString().split('T')[0]}
-- Description: TODO - Add description

BEGIN;

-- TODO: Add your migration SQL here

COMMIT;

-- Validation
DO $$
BEGIN
    RAISE NOTICE 'Migration ${filename} completed successfully';
END $$;
`;

    const rollbackTemplate = `-- SPEK Platform v2 - Rollback for ${name}
-- Rollback: ${rollbackFilename}
-- Created: ${new Date().toISOString().split('T')[0]}
-- Description: Rolls back ${filename}

BEGIN;

-- TODO: Add your rollback SQL here

COMMIT;

-- Validation
DO $$
BEGIN
    RAISE NOTICE 'Rollback ${rollbackFilename} completed successfully';
END $$;
`;

    fs.writeFileSync(migrationPath, template);
    fs.writeFileSync(rollbackPath, rollbackTemplate);

    console.log('✅ Created migration:');
    console.log(`   ${migrationPath}`);
    console.log(`   ${rollbackPath}`);
}

// ============================================
// CLI INTERFACE
// ============================================

async function main() {
    const args = process.argv.slice(2);
    const command = args[0];

    if (!command) {
        console.log('Usage:');
        console.log('  node scripts/migrate.js up              # Run all pending migrations');
        console.log('  node scripts/migrate.js down            # Rollback last migration');
        console.log('  node scripts/migrate.js down --all      # Rollback all migrations');
        console.log('  node scripts/migrate.js status          # Show migration status');
        console.log('  node scripts/migrate.js create <name>   # Create new migration template');
        process.exit(1);
    }

    switch (command) {
        case 'up':
            await migrateUp();
            break;

        case 'down':
            const all = args.includes('--all');
            await migrateDown({ all });
            break;

        case 'status':
            await showStatus();
            break;

        case 'create':
            createMigration(args[1]);
            break;

        default:
            console.error(`❌ Unknown command: ${command}`);
            process.exit(1);
    }
}

// Run CLI
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Fatal error:', error);
        process.exit(1);
    });
}

module.exports = { migrateUp, migrateDown, showStatus };
