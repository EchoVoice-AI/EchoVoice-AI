import type { CardProps } from '@mui/material/Card';
import type { ISegmentorCard } from 'src/types/segmentor';

import { useState } from 'react';
import { useSWRConfig } from 'swr';
import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
import ListItemText from '@mui/material/ListItemText';
import { Switch, FormControlLabel } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';

import { fShortenNumber } from 'src/utils/format-number';

import { AvatarShape } from 'src/assets/illustrations';
import axiosInstance, { fetcher, endpoints } from 'src/lib/axios';

import { Image } from 'src/components/image';
import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------

type Props = CardProps & {
  segment: ISegmentorCard;
};

export function SegmentorCard({ segment, sx, ...other }: Props) {
  // Component-level loading indicator while mutate runs
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const { mutate, cache } = useSWRConfig();

  const handleToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    const key = endpoints.segmentor.list;

    // Read current cached data (may be undefined or wrapped). Coerce to array
    const raw = cache.get(key);
    let currentArray: any[] = [];
    if (Array.isArray(raw)) {
      currentArray = raw as any[];
    } else if (raw && Array.isArray((raw as any).data)) {
      currentArray = (raw as any).data as any[];
    } else if (raw && Array.isArray((raw as any).value)) {
      currentArray = (raw as any).value as any[];
    } else {
      currentArray = [];
    }

    // Build optimistic payload: set enabled for this segment locally
    const optimisticData = currentArray.map((s: any) => (s.id === segment.id ? { ...s, enabled: newValue } : s));

    setIsUpdating(true);

    // Use mutate with optimisticData and rollbackOnError so SWR updates UI immediately
    const mutatePromise = mutate(
      key,
      async () => {
        // Perform the server update
        await axiosInstance.patch(`${endpoints.segmentor.update}${segment.id}`, { enabled: newValue });

        // Fetch latest from server and return to populate cache
        const refreshed = await fetcher(key);
        return refreshed;
      },
      {
        optimisticData,
        rollbackOnError: true,
        revalidate: false,
        populateCache: true,
      }
    );

    try {
      toast.promise(mutatePromise, {
        loading: newValue ? 'Enabling...' : 'Disabling...',
        success: newValue ? 'Segment enabled' : 'Segment disabled',
        error: 'Failed to update segment',
      });

      await mutatePromise;
    } catch (err) {
      console.error('Failed to PATCH segment enabled state', err);
    } finally {
      setIsUpdating(false);
    }
  };
  return (
    <Card sx={[{ textAlign: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]} {...other}>
      <Box sx={{ position: 'relative' }}>
        <AvatarShape
          sx={{
            left: 0,
            right: 0,
            zIndex: 10,
            mx: 'auto',
            bottom: -26,
            position: 'absolute',
          }}
        />

        <Avatar
          alt={segment.name}
          src={segment.avatarUrl}
          sx={{
            left: 0,
            right: 0,
            width: 64,
            height: 64,
            zIndex: 11,
            mx: 'auto',
            bottom: -32,
            position: 'absolute',
          }}
        />

        <Image
          src={segment.coverUrl}
          alt={segment.coverUrl}
          ratio="16/9"
          slotProps={{
            overlay: {
              sx: (theme) => ({
                bgcolor: varAlpha(theme.vars.palette.common.blackChannel, 0.48),
              }),
            },
          }}
        />
      </Box>

      <ListItemText
        sx={{ mt: 7, mb: 1 }}
        primary={segment.name}
        secondary={segment.role}
        slotProps={{
          primary: { sx: { typography: 'subtitle1' } },
          secondary: { sx: { mt: 0.5 } },
        }}
      />

      <Box
        sx={{
          mb: 2.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <FormControlLabel
          control={<Switch checked={!!segment.enabled} onChange={handleToggle} disabled={isUpdating} />}
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {segment.enabled ? 'Enabled' : 'Disabled'}
              {isUpdating && <CircularProgress size={14} sx={{ ml: 1 }} />}
            </Box>
          }
          labelPlacement="end"
        />
      </Box>

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
          { label: 'Priority', value: segment.priority },
          { label: 'Following', value: 400 },
          { label: 'Total post', value: 235 },
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
