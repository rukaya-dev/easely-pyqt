CREATE POLICY "roles_permissions_policy"
ON public.roles_permissions
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
