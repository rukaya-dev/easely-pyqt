CREATE POLICY "appointment_types_policy"
ON public.appointment_types
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
