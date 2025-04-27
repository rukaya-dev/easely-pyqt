CREATE POLICY "patients_policy"
ON public.patients
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
