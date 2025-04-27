create table log_audit (
  log_id  serial not null primary key,
  action_type character varying,
  model_name character varying,
  data text,
  changed_by character varying,
  change_date timestamp default now() not null,
  status character varying
);
