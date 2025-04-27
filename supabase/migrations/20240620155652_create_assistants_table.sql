create table assistants (
  assistant_id serial not null primary key,
  first_name character varying not null,
  last_name character varying not null,
  role character varying not null,
  qualifications text,
  phone_number character varying,
  email character varying,
  image_id integer references images (image_id),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  address text
);
