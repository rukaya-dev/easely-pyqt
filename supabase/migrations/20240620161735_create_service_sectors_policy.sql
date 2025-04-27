CREATE POLICY "service_sectors_policy"
ON public.service_sectors
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
