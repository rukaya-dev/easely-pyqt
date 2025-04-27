create table templates (
  template_id serial not null primary key,
  name character varying not null UNIQUE ,
  description text,
  content text not null,
  category_id character varying references categories (name),
  template_options text[],
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);

CREATE POLICY "templates_policy"
ON public.templates
FOR ALL
TO authenticated
USING (user_has_permission('report_workshop_access'::text))
WITH CHECK (user_has_permission('report_workshop_access'::text));