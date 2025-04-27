CREATE POLICY "patients_history_change_logs_policy"
ON public.patients_history_change_logs
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
