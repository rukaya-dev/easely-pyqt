CREATE POLICY "doctors_policy"
ON public.doctors
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
