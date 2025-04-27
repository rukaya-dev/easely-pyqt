-- Insert roles
INSERT INTO public.roles (role_name)
VALUES ('superadmin'), ('admin');

-- Insert permissions
INSERT INTO public.permissions (permission_name, description, permission_slug)
VALUES
    ('Patients Access', NULL, 'patients_access'),
    ('Settings Access', NULL, 'settings_access'),
    ('Report Workshop Access', NULL, 'report_workshop_access'),
    ('Log Audit Access', NULL, 'log_audit_access'),
    ('Appointments Access', NULL, 'appointments_access'),
    ('Staff Access', NULL, 'staff_access'),
    ('Billings Access', NULL, 'billings_access'),
    ('Report Access', NULL, 'reports_access'),
    ('Dashboard Access', NULL, 'dashboard_access');

-- Insert role-permission mappings for superadmin (role_id = 1) and admin (role_id = 2)
INSERT INTO public.roles_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM public.roles r
CROSS JOIN public.permissions p
WHERE r.role_name IN ('superadmin', 'admin')
AND NOT EXISTS (
    SELECT 1
    FROM public.roles_permissions rp
    WHERE rp.role_id = r.role_id
    AND rp.permission_id = p.permission_id
);

-- Enable row-level security on the database
ALTER DATABASE postgres SET row_security = ON;

-- Enable row-level security for all tables in the public schema
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(table_record.tablename) || ' ENABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;

-- Enable row-level security for all tables in the storage schema
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'storage'
    LOOP
        EXECUTE 'ALTER TABLE storage.' || quote_ident(table_record.tablename) || ' ENABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;

-- Insert appointment statuses
INSERT INTO public.appointment_statuses (status_name)
VALUES
    ('arrived'),
    ('no-show'),
    ('canceled'),
    ('re-scheduled'),
    ('rejected'),
    ('in-room'),
    ('invoiced'),
    ('ready-to-invoice'),
    ('in-with-doctor'),
    ('scheduled'),
    ('expired');

-- Insert appointment types
INSERT INTO public.appointment_types (type_name, description)
VALUES
    ('follow-up', NULL),
    ('consultation', NULL);

-- Insert clinic information
INSERT INTO public.clinics (
    name,
    address,
    phone_number,
    email,
    website,
    fax_number,
    contact_person,
    contact_person_phone,
    contact_person_email,
    services_offered,
    clinic_hours,
    registration_number,
    latitude,
    longitude,
    logo_image_path
) VALUES (
    'Health Plus Clinic',
    '123 Wellness Ave, Suite 100, Springfield',
    '123-456-7890',
    'info@healthplusclinic.com',
    'http://www.healthplusclinic.com',
    '123-456-7891',
    'Dr. John Doe',
    '123-456-7892',
    'johndoe@healthplusclinic.com',
    'General Medicine, Pediatrics, Dermatology',
    NULL,
    'HPC12345',
    37.7749,
    -122.4194,
    NULL
);

-- Insert report layout
INSERT INTO public.report_layouts (name, content)
VALUES ('report_header_layout', '');

-- Insert service
INSERT INTO public.services (name)
VALUES ('Ultrasound');