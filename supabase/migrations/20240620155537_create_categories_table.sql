create table categories (
  category_id serial not null primary key,
  name character varying not null UNIQUE,
  description text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
