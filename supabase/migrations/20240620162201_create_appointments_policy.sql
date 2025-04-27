CREATE POLICY "appointments_policy"
ON public.appointments
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
