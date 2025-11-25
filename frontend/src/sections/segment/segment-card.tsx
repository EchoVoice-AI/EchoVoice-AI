import type { CardProps } from '@mui/material/Card';
import type { ISegmentorCard } from 'src/types/segmentor';

import { useState } from 'react';
import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
import ListItemText from '@mui/material/ListItemText';
import { Switch, FormControlLabel } from '@mui/material';

import { fShortenNumber } from 'src/utils/format-number';

import { AvatarShape } from 'src/assets/illustrations';
import axiosInstance, { endpoints } from 'src/lib/axios';
import { mutate } from 'swr';
import CircularProgress from '@mui/material/CircularProgress';

import { Image } from 'src/components/image';
import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------

type Props = CardProps & {
  segment: ISegmentorCard;
};

export function SegmentorCard({ segment, sx, ...other }: Props) {
  const [enabled, setEnabled] = useState<boolean>(!!segment.enabled);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  const handleToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;

    // Optimistic update
    setEnabled(newValue);
    setIsUpdating(true);

    const url = `${endpoints.segmentor.update}${segment.id}`;
    const promise = axiosInstance.patch(url, { enabled: newValue });

    try {
      toast.promise(promise, {
        loading: newValue ? 'Enabling...' : 'Disabling...',
        success: newValue ? 'Segment enabled' : 'Segment disabled',
        error: 'Failed to update segment',
      });

      await promise;

      // Revalidate the segments list so the parent view reflects server state
      await mutate(endpoints.segmentor.list);
    } catch (err) {
      // Revert optimistic update on error
      setEnabled(!newValue);
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
          control={<Switch checked={enabled} onChange={handleToggle} disabled={isUpdating} />}
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {enabled ? 'Enabled' : 'Disabled'}
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
