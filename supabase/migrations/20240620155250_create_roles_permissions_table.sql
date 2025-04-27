create table roles_permissions (
  id serial not null primary key,
  role_id integer references roles (role_id),
  permission_id integer references permissions (permission_id)
);
