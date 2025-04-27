create table doctors (
  doctor_id serial not null primary key,
  first_name character varying not null,
  last_name character varying not null,
  specialty character varying,
  qualifications text,
  phone_number character varying,
  email character varying,
  room_number character varying,
  image_id integer references images (image_id),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  address text
);
