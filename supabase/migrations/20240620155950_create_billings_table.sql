
create table billings (
  billing_id serial not null primary key,
  patient_id integer references patients (patient_id),
  appointment_id integer references appointments (appointment_id),
  total_amount numeric not null,
  insurance_provider character varying,
  insurance_policy_number character varying,
  coverage_percentage numeric,
  net_amount numeric not null,
  billing_date timestamp default now() not null,
  status character varying not null,
  payment_method character varying not null,
  notes text null,
  updated_at timestamp with time zone
);
