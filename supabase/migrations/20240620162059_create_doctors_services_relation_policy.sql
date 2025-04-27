CREATE POLICY "doctors_services_relation_policy"
ON public.doctors_services_relation
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
