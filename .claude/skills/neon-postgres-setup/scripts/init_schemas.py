#!/usr/bin/env python3
"""Initialize LearnFlow database schemas for Neon PostgreSQL.

Schema design matches actual LearnFlow production:
- Better Auth auto-creates: user, session, account, verification tables
  (user table includes custom 'role' field added via additionalFields)
- Custom tables: exercises, submissions, learning_events, struggles
- Dapr state store tables: state, dapr_metadata (created by Dapr runtime)

Important: Neon requires SSL. Connection string must include sslmode=require
or the script configures SSL explicitly.
"""
import sys, argparse
try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed: pip install psycopg2-binary")
    sys.exit(1)

# Custom LearnFlow schemas (NOT user tables - Better Auth handles those)
# Better Auth auto-creates: user, session, account, verification
# Better Auth user table includes: id, name, email, emailVerified, image, createdAt, updatedAt, role
SCHEMA_SQL = """
-- LearnFlow custom tables (Better Auth manages user/session/account/verification)

CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50) DEFAULT 'beginner',
    module_id VARCHAR(50) DEFAULT 'mod-1',
    topic VARCHAR(255) DEFAULT '',
    starter_code TEXT DEFAULT '',
    expected_output TEXT DEFAULT '',
    hints JSONB DEFAULT '[]',
    test_cases JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    exercise_id UUID,
    code TEXT NOT NULL,
    output TEXT DEFAULT '',
    error TEXT DEFAULT '',
    score FLOAT DEFAULT 0,
    passed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    service VARCHAR(100) DEFAULT '',
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS struggles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    struggle_type VARCHAR(100) NOT NULL,
    error_type VARCHAR(100) DEFAULT '',
    error_count INTEGER DEFAULT 1,
    details JSONB DEFAULT '{}',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_exercise ON submissions(exercise_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_user ON learning_events(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_type ON learning_events(event_type);
CREATE INDEX IF NOT EXISTS idx_struggles_user ON struggles(user_id);
CREATE INDEX IF NOT EXISTS idx_exercises_module ON exercises(module_id);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty);
"""


def init_schemas(connection_string):
    """Initialize LearnFlow schemas on Neon PostgreSQL."""
    try:
        # Neon requires SSL - ensure it's configured
        conn_str = connection_string
        if "sslmode" not in conn_str:
            conn_str += "?sslmode=require"

        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        print("Connected to Neon PostgreSQL (SSL)")

        # Create custom tables
        cur.execute(SCHEMA_SQL)
        conn.commit()

        # List all tables to verify
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        print(f"\n✓ LearnFlow schemas initialized")
        print(f"  Custom tables created: exercises, submissions, learning_events, struggles")
        print(f"  Indexes created for user_id, exercise_id, event_type, module_id, difficulty")
        print(f"\n  All tables in database ({len(tables)}):")
        for t in tables:
            # Mark Better Auth tables
            if t in ('user', 'session', 'account', 'verification'):
                print(f"    - {t} (Better Auth - auto-managed)")
            elif t in ('state', 'dapr_metadata'):
                print(f"    - {t} (Dapr state store - auto-managed)")
            else:
                print(f"    - {t} (LearnFlow custom)")

        print(f"\n  Note: Better Auth creates user/session/account/verification tables")
        print(f"  automatically on first auth request. The 'user' table includes a")
        print(f"  custom 'role' field (default: 'student') configured in auth.ts.")
        print(f"\n  Dapr creates state/dapr_metadata tables when services first use")
        print(f"  the state store component.")

        return 0
    except Exception as e:
        print(f"Schema initialization failed: {e}")
        if "SSL" in str(e).upper() or "ssl" in str(e):
            print(f"  Tip: Neon requires SSL. Ensure connection string includes ?sslmode=require")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize LearnFlow schemas on Neon PostgreSQL")
    parser.add_argument("--connection-string", required=True,
                       help="Neon PostgreSQL connection string (with sslmode=require)")
    args = parser.parse_args()
    sys.exit(init_schemas(args.connection_string))
