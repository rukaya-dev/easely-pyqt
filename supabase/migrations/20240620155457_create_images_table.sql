create table images (
  image_id serial not null primary key,
  file_path text not null,
  image_type text,
  description text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
