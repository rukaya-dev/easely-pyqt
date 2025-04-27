CREATE POLICY "patients_trash_policy"
ON public.patients_trash
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
