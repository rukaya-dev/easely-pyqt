
create table doctors_schedules (
  schedule_id serial not null primary key,
  doctor_id integer references doctors (doctor_id),
  day character varying,
  time_slots text[],
  doctor_service_relation_id integer references doctors_services_relation (doctor_service_relation_id),
  time_increment smallint not null,
  time_increment_unit character varying not null,
  start_time time not null,
  end_time time not null
);
