import type { BoxProps } from '@mui/material/Box';
import type { CardProps } from '@mui/material/Card';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Rating from '@mui/material/Rating';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';
import { svgIconClasses } from '@mui/material/SvgIcon';

import { fDate } from 'src/utils/format-time';
import { fShortenNumber } from 'src/utils/format-number';

import { Label } from 'src/components/label';
import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';

// ----------------------------------------------------------------------

// ----------------------------------------------------------------------

type Props = CardProps & {
  title?: string;
  subheader?: string;
  list: [];
};

export function AppTopRelated({ title, subheader, list, sx, ...other }: Props) {

  return (
    <Card sx={sx} {...other}>
      <CardHeader title={title} subheader={subheader} sx={{ mb: 3 }} />

      <Scrollbar sx={{ minHeight: 384 }}>
        <Box
          sx={{
            p: 3,
            gap: 3,
            minWidth: 360,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {list.map((item,index) => (
            <Item key={index} item={item} />
          ))}
        </Box>
      </Scrollbar>
    </Card>
  );
}

// ----------------------------------------------------------------------

type ItemProps = BoxProps & {
  item: Props['list'][number];
};

function Item({ item, sx, ...other }: ItemProps) {
  return (
    <Box
      sx={[{ gap: 2, display: 'flex', alignItems: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]}
      {...other}
    >
      <div>
        <Box
          sx={{
            mb: 1,
            gap: 1,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Typography variant="subtitle2" noWrap>
            James Smith
          </Typography>

          <Label color="success" sx={{ height: 20 }}>
            Pending
          </Label>
        </Box>

        <Stack
          divider={
            <Box
              sx={{
                width: 4,
                height: 4,
                borderRadius: '50%',
                bgcolor: 'text.disabled',
              }}
            />
          }
          sx={{
            gap: 1,
            flexDirection: 'row',
            alignItems: 'center',
            typography: 'caption',
          }}
        >
          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Iconify width={16} icon="solar:download-bold" sx={{ color: 'text.disabled' }} />
            {30}
          </Box>

          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            {fDate('2024-01-01T00:00:00Z')}
          </Box>
          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Iconify width={16} icon="heroicons:server-solid" sx={{ color: 'text.disabled' }} />
            {fDate('2024-01-15T00:00:00Z')}
          </Box>

          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Rating
              readOnly
              size="small"
              precision={0.5}
              name="reviews"
              value={4.5}
              max={1}
              sx={{ [` .${svgIconClasses.root}`]: { width: 16, height: 16 } }}
            />
            {fShortenNumber(0)}
          </Box>
        </Stack>
      </div>
    </Box>
  );
}
