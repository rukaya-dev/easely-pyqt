CREATE POLICY "roles_policy"
ON public.roles
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
