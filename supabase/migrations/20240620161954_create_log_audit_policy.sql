CREATE POLICY "log_audit_policy"
ON public.log_audit
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
