
create table patients_trash (
  trash_id serial not null primary key,
  patient_id integer references patients (patient_id),
  deleted_at timestamp with time zone default now(),
  deleted_by text not null,
  patient_info jsonb not null
);
