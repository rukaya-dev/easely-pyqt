create table reports_trash (
  trash_id serial not null primary key,
  report_id integer references reports (report_id),
  patient_id integer references patients (patient_id),
  report_info jsonb not null,
  deleted_by varchar not null,
  deleted_at timestamp with time zone default now()
);


CREATE POLICY "reports_trash_policy"
ON public.reports_trash
FOR ALL
TO authenticated
USING (user_has_permission('reports_access'::text))
WITH CHECK (user_has_permission('reports_access'::text));