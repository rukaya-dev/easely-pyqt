CREATE POLICY "services_policy"
ON public.services
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
