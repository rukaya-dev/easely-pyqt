create table reports (
  report_id serial not null primary key,
  patient_id integer references patients (patient_id),
  appointment_id integer references appointments (appointment_id),
  referring_doctor_id integer references referring_doctors (doctor_id),
  template_name character varying references templates (name),
  report_title character varying,
  report_content text not null,
  status character varying not null default 'Drafted',
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone,
  deleted_at timestamp with time zone,
  category character varying references categories (name)
);

CREATE POLICY "reports_policy"
ON public.reports
FOR ALL
TO authenticated
USING (user_has_permission('reports_access'::text))
WITH CHECK (user_has_permission('reports_access'::text));