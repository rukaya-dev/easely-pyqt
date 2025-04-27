CREATE POLICY "billings_policy"
ON public.billings
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
