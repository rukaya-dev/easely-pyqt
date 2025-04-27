CREATE POLICY "categories_policy"
ON public.categories
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
