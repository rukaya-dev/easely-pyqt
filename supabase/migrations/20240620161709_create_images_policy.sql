CREATE POLICY "images_policy"
ON public.images
FOR ALL
TO authenticated
USING (
  True
)
WITH CHECK (
  True
);
