import { z } from 'zod'

export const suggestFormSchema = z.object({
  replacement: z.string().trim().min(1, 'Replacement text is required'),
  reason: z.string().max(500, 'Keep the reason under 500 characters'),
  name: z.string().max(100, 'Keep the name under 100 characters'),
})

export type SuggestFormValues = z.infer<typeof suggestFormSchema>
