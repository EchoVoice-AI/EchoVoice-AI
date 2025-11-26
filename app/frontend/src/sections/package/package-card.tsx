import type { CardProps } from '@mui/material/Card';
import type { IPackageCard } from 'src/types/package';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Divider from '@mui/material/Divider';
import ListItemText from '@mui/material/ListItemText';

import { fShortenNumber } from 'src/utils/format-number';



// ----------------------------------------------------------------------

type Props = CardProps & {
  pack: IPackageCard;
};

export function PackageCard({ pack, sx, ...other }: Props) {
  return (
    <Card sx={[{ textAlign: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]} {...other}>

      <ListItemText
        sx={{ mt: 7, mb: 1 }}
        primary={pack.name}
        secondary={pack.status}
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
            { label: 'Subscribers', value: pack.subscribers },
            { label: 'Data Limit', value: pack.data_limit },
            { label: 'Rate Limit', value: pack.rate_limit },
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
