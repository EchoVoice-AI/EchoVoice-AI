import type { GridCellParams } from '@mui/x-data-grid';

import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import Avatar from '@mui/material/Avatar';
import ListItemText from '@mui/material/ListItemText';

import { RouterLink } from 'src/routes/components';

import { fTime, fDate } from 'src/utils/format-time';
import { fNumber, fCurrency } from 'src/utils/format-number';

import { Label } from 'src/components/label';

// ----------------------------------------------------------------------

type ParamsProps = {
  params: GridCellParams;
};

export function RenderCellPrice({ params }: ParamsProps) {
  return fCurrency(params.row.leave_days);
}

export function RenderCellPublish({ params }: ParamsProps) {
  return (
    <Label variant="soft" color={params.row.status === 'Approved' ? 'success' : 'default'}>
      {params.row.status}
    </Label>
  );
}

export function RenderCellBalanceType({ params }: ParamsProps) {
  return (
    <Box sx={{ width: 1, typography: 'caption', color: 'text.secondary' }}>
      {params.row.leave_type_name}
    </Box>
  );
}
export function RenderCellCreatedAt({ params }: ParamsProps) {
  return (
    <Box sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
      <span>{fDate(params.row.start_date)}</span>
      <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
        {fTime(params.row.start_date)}
      </Box>
    </Box>
  );
}

export function RenderCellEndedAt({ params }: ParamsProps) {
  return (
    <Box sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
      <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
        {fTime(params.row.end_date)}
      </Box>
    </Box>
  );
}
export function RenderCellTotalDays({ params }: ParamsProps) {
  return (
    <Box sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
      <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
        {fNumber(params.row.total_days)}
      </Box>
    </Box>
  );
}

export function RenderCellRemainingDays({ params }: ParamsProps) {
  return (
    <Box sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
      <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
        {fNumber(params.row.remaining_days)}
      </Box>
    </Box>
  );
}


export function RenderCellUsedDays({ params }: ParamsProps) {
  return (
    <Box sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
      <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
        {fNumber(params.row.used_days)}
      </Box>
    </Box>
  );
}
export function RenderCellStock({ params }: ParamsProps) {
  return (
    <Box sx={{ width: 1, typography: 'caption', color: 'text.secondary' }}>
      {params.row.leave_type}
    </Box>
  );
}

export function RenderCellProduct({ params, href }: ParamsProps & { href: string }) {
  return (
    <Box
      sx={{
        py: 2,
        gap: 2,
        width: 1,
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <Avatar
        alt={params.row.employee}
        src={params.row.coverUrl}
        variant="rounded"
        sx={{ width: 64, height: 64 }}
      />

      <ListItemText
        primary={
          <Link component={RouterLink} href={href} color="inherit">
            {params.row.id}
          </Link>
        }
        secondary={params.row.leave_type}
        slotProps={{
          primary: { noWrap: true },
          secondary: { sx: { color: 'text.disabled' } },
        }}
      />
    </Box>
  );
}
export function RenderCellBalance({ params, href }: ParamsProps & { href: string }) {
  return (
    <Box
      sx={{
        py: 2,
        gap: 2,
        width: 1,
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {params.row.employee_name}
    </Box>
  );
}
