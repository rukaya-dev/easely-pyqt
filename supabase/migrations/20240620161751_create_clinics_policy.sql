CREATE POLICY "clinics_policy"
ON public.clinics
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
