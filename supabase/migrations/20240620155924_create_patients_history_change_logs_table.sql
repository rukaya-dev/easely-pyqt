
create table patients_history_change_logs (
  change_id serial not null primary key,
  patient_id integer references patients (patient_id),
  change_type character varying not null,
  changed_by text not null,
  change_date timestamp with time zone default now(),
  data_before text,
  data_after text,
  details text
);
