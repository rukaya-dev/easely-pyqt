create table service_sectors (
  sector_id serial not null primary key,
  sector_name character varying not null,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
