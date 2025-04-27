create table options (
  option_id serial not null primary key,
  parent_option_id integer,
  name character varying not null,
  option_structure json not null,
  type character varying not null,
  slug character varying not null,
  category_id character varying references categories (name),
  description text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);
CREATE POLICY "options_policy"
ON public.options
FOR ALL
TO authenticated
USING (user_has_permission('report_workshop_access'::text))
WITH CHECK (user_has_permission('report_workshop_access'::text));