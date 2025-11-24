import type { CardProps } from '@mui/material/Card';
import type { IVoucherCard } from 'src/types/voucher';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Divider from '@mui/material/Divider';
import ListItemText from '@mui/material/ListItemText';

import { fShortenNumber } from 'src/utils/format-number';



// ----------------------------------------------------------------------

type Props = CardProps & {
  voucher: IVoucherCard;
};

export function VoucherCard({ voucher, sx, ...other }: Props) {
  return (
    <Card sx={[{ textAlign: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]} {...other}>

      <ListItemText
        sx={{ mt: 7, mb: 1 }}
        primary={voucher.name}
        secondary={voucher.status}
        slotProps={{
          primary: { sx: { typography: 'subtitle1' } },
          secondary: { sx: { mt: 0.5 } },
        }}
      />

      <Divider sx={{ borderStyle: 'dashed' }} />

      <Box
        sx={{
          py: 3,
          display: 'grid',
          typography: 'subtitle1',
          gridTemplateColumns: 'repeat(3, 1fr)',
        }}
      >
        {[
            { label: 'Subscribers', value: voucher.subscribers },
            { label: 'Data Limit', value: voucher.data_limit },
            { label: 'Rate Limit', value: voucher.rate_limit },
          ].map((stat) => (
          <Box key={stat.label} sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
            <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
              {stat.label}
            </Box>
            {fShortenNumber(stat.value)}
          </Box>
        ))}
      </Box>
    </Card>
  );
}
