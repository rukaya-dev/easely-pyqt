create table services (
  service_id serial not null primary key,
  name character varying UNIQUE not null,
  description text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
