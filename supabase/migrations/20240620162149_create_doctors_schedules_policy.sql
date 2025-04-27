CREATE POLICY "doctors_schedules_policy"
ON public.doctors_schedules
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
