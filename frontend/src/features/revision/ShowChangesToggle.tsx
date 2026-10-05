import FormControlLabel from '@mui/material/FormControlLabel'
import Switch from '@mui/material/Switch'

interface Props {
  checked: boolean
  onChange: (v: boolean) => void
}

export function ShowChangesToggle({ checked, onChange }: Props) {
  return (
    <FormControlLabel
      control={<Switch size="small" checked={checked} onChange={(_, v) => onChange(v)} />}
      label="Show changes"
      data-testid="show-changes"
      sx={{ fontFamily: 'Inter, system-ui, sans-serif' }}
    />
  )
}
