create table report_layouts (
  layout_id serial not null primary key,
  name character varying not null,
  content text,
  created_at timestamp with time zone default now()
);
CREATE POLICY "report_layouts_policy"
ON public.report_layouts
FOR ALL
TO authenticated
USING (user_has_permission('report_workshop_access'::text))
WITH CHECK (user_has_permission('report_workshop_access'::text));

