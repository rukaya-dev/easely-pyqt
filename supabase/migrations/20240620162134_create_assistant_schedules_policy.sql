CREATE POLICY "assistant_schedules_policy"
ON public.assistant_schedules
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
