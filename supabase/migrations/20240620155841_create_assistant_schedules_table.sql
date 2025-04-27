create table assistant_schedules (
  assistant_schedule_id serial not null primary key,
  assistant_id integer references assistants (assistant_id),
  doctor_id integer references doctors (doctor_id),
  day character varying,
  start_time time,
  end_time time,
  additional_data jsonb
);
