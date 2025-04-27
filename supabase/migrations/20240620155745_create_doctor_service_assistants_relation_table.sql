create table doctor_service_assistants_relation (
  doctor_service_assistants_id serial not null primary key,
  assistant_id integer references assistants (assistant_id),
  doctor_service_relation_id integer references doctors_services_relation (doctor_service_relation_id),
  additional_data jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
