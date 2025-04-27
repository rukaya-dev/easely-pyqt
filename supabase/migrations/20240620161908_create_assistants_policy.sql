CREATE POLICY "assistants_policy"
ON public.assistants
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
