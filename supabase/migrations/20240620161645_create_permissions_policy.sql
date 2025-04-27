CREATE POLICY "permissions_policy"
ON public.permissions
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
