create table doctors_services_relation (
  doctor_service_relation_id serial not null primary key,
  doctor_id integer references doctors (doctor_id),
  doctor_service_cost numeric not null,
  additional_data jsonb,
  doctor_service_status character varying not null,
  doctor_service_duration integer not null,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  service_name character varying references services (name)
);
