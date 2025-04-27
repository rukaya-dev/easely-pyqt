DO $$
DECLARE
    r RECORD;
BEGIN
    -- Loop through all tables in the public schema
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        -- Drop each table
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;


DO $$
DECLARE
    r RECORD;
BEGIN
    -- Loop through all views in the public schema
    FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = 'public') LOOP
        -- Drop each view
        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
    END LOOP;
END $$;

DO $$
DECLARE
    r RECORD;
BEGIN
    -- Loop through all policies in the public schema
    FOR r IN (
        SELECT
            p.policyname,
            t.schemaname,
            t.tablename
        FROM
            pg_policies p
        JOIN
            pg_tables t
        ON
            p.tablename = t.tablename
        WHERE
            t.schemaname = 'public'
    ) LOOP
        -- Drop each policy
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename);
    END LOOP;
END $$;


DO $$
DECLARE
    r RECORD;
BEGIN
    -- Loop through all functions in the public schema
    FOR r IN (
        SELECT routine_name, routine_schema
        FROM information_schema.routines
        WHERE routine_schema = 'public'
    ) LOOP
        -- Drop each function
        EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.routine_schema) || '.' || quote_ident(r.routine_name) || ' CASCADE';
    END LOOP;
END $$;
