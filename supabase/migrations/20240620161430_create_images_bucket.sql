insert into storage.buckets
  (id, name, public)
values
  ('images', 'images', true);


CREATE POLICY "storage_buckets_policy"
ON storage.buckets
FOR ALL
TO authenticated
USING (
    user_has_permission('settings_access'::text) AND
    id = 'images'
)
WITH CHECK (
    user_has_permission('settings_access'::text) AND
    id = 'images'
);

CREATE POLICY "storage_objects_policy"
ON storage.objects
FOR ALL
TO authenticated
USING (user_has_permission('settings_access'::text))
WITH CHECK (user_has_permission('settings_access'::text));