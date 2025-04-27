CREATE POLICY "doctor_service_assistants_relation_policy"
ON public.doctor_service_assistants_relation
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
