create table permissions (
  permission_id serial not null primary key,
  permission_name character varying not null,
  description text,
  permission_slug character varying not null
);
