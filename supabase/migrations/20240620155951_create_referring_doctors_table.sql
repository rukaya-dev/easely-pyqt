
create table referring_doctors (
  doctor_id serial not null primary key,
  first_name character varying not null,
  last_name character varying not null,
  specialty character varying,
  phone_number character varying,
  email character varying,
  address text,
  notes text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  category character varying references categories (name)
);

CREATE POLICY "referring_doctors_policy"
ON public.referring_doctors
FOR ALL
TO authenticated
USING (user_has_permission('staff_access'::text))
WITH CHECK (user_has_permission('staff_access'::text));