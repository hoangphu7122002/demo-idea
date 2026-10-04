import { zodResolver } from '@hookform/resolvers/zod'
import Button from '@mui/material/Button'
import Paper from '@mui/material/Paper'
import Popper from '@mui/material/Popper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useForm } from 'react-hook-form'
import { FormTextField } from '../../components/form/FormTextField'
import { useMutationToast } from '../../hooks/useMutationToast'
import type { SuggestionAnchor } from './anchor'
import { useSubmitSuggestionMutation } from './suggestApi'
import { suggestFormSchema, type SuggestFormValues } from './suggestSchema'

const EMPTY: SuggestFormValues = { replacement: '', reason: '', name: '' }

interface Props {
  slug: string
  anchor: SuggestionAnchor
  onClose: () => void
}

export function SuggestPopup({ slug, anchor, onClose }: Props) {
  const [submit] = useSubmitSuggestionMutation()
  const run = useMutationToast()
  const { control, handleSubmit, formState } = useForm<SuggestFormValues>({
    resolver: zodResolver(suggestFormSchema),
    defaultValues: EMPTY,
  })
  // Virtual element so the popup sits next to the selected text.
  const anchorEl = { getBoundingClientRect: () => anchor.rect }

  const onSubmit = handleSubmit(async (v) => {
    const body = {
      original_text: anchor.original_text,
      replacement: v.replacement.trim(),
      reason: v.reason.trim() || null,
      name: v.name.trim() || null,
      anchor_start: anchor.anchor_start,
      anchor_end: anchor.anchor_end,
      paragraph_id: anchor.paragraph_id,
    }
    if (await run(submit({ slug, body }).unwrap(), { success: 'Suggestion sent. Thank you!', error: 'Could not send suggestion' })) onClose()
  })

  return (
    <Popper open anchorEl={anchorEl} placement="bottom-start" sx={{ zIndex: 'modal' }} modifiers={[{ name: 'offset', options: { offset: [0, 8] } }]}>
      <Paper
        component="form"
        elevation={8}
        data-testid="suggest-popup"
        aria-label="Suggest a fix"
        onSubmit={onSubmit}
        onKeyDown={(e) => e.key === 'Escape' && onClose()}
        noValidate
        sx={{ p: 2, width: 340, bgcolor: 'background.paper' }}
      >
        <Stack spacing={1.5}>
          <Typography variant="caption" color="text.secondary" data-testid="suggest-level">
            {anchor.level === 'span' ? 'Suggest a fix for' : 'Suggest a fix in this paragraph'}
          </Typography>
          <Typography variant="body2" sx={{ fontStyle: 'italic', maxHeight: 64, overflow: 'auto' }} data-testid="suggest-original">
            “{anchor.original_text}”
          </Typography>
          <FormTextField control={control} name="replacement" label="Replacement" required autoFocus multiline minRows={2} slotProps={{ htmlInput: { 'data-testid': 'suggest-replacement' } }} />
          <FormTextField control={control} name="reason" label="Reason (optional)" slotProps={{ htmlInput: { 'data-testid': 'suggest-reason' } }} />
          <FormTextField control={control} name="name" label="Your name (optional)" slotProps={{ htmlInput: { 'data-testid': 'suggest-name' } }} />
          <Stack direction="row" spacing={1} sx={{ justifyContent: 'flex-end' }}>
            <Button onClick={onClose} color="inherit" data-testid="suggest-cancel">
              Cancel
            </Button>
            <Button type="submit" variant="contained" loading={formState.isSubmitting} data-testid="suggest-submit">
              Submit
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </Popper>
  )
}
