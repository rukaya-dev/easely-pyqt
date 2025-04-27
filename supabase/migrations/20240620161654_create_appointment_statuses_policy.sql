CREATE POLICY "appointment_statuses_policy"
ON public.appointment_statuses
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
