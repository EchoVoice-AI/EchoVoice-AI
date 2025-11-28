import type { CardProps } from '@mui/material/Card';
import type { ISegmentorCard } from 'src/types/segmentor';

import { useState } from 'react';
import { m } from 'framer-motion';
import { useSWRConfig } from 'swr';
import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import Dialog from '@mui/material/Dialog';
import Button from '@mui/material/Button';
import SvgIcon from '@mui/material/SvgIcon';
import Divider from '@mui/material/Divider';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import DialogTitle from '@mui/material/DialogTitle';
import ListItemText from '@mui/material/ListItemText';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { Switch, FormControlLabel } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';

import { fShortenNumber } from 'src/utils/format-number';

import { endpoints } from 'src/lib/axios';
import { AvatarShape } from 'src/assets/illustrations';

import { Image } from 'src/components/image';
import { toast } from 'src/components/snackbar';


// ----------------------------------------------------------------------

type Props = CardProps & {
  segment: ISegmentorCard;
  onUpdate?: (segment: ISegmentorCard) => void;
};

export function SegmentorCard({ segment, sx, onUpdate, ...other }: Props) {
  // Component-level loading indicator while mutate runs
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const { mutate, cache } = useSWRConfig();
  // If parent passed onUpdate, prefer updating parent state directly for mock-driven demo
  const callParentUpdate = (updated: ISegmentorCard) => {
    if (typeof onUpdate === 'function') {
      try {
        onUpdate(updated);
        return true;
      } catch (err) {
        // swallow errors from parent callback
        console.error('onUpdate callback failed', err);
      }
    }
    return false;
  };

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
    // For demo purposes we simulate a successful PATCH (HTTP 200) and return the optimistic data.
    const mutatePromise = mutate(
      key,
      async () => {
        // simulate network latency
        await new Promise((r) => setTimeout(r, 300));
        return optimisticData;
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
      // If parent provided onUpdate, notify it with the updated segment
      try {
        const updatedSegment = optimisticData.find((s: any) => s.id === segment.id);
        if (updatedSegment) callParentUpdate(updatedSegment as ISegmentorCard);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (err) {
        /* ignore */
      }
    } catch (err) {
      console.error('Failed to PATCH segment enabled state', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleOpenSettings = () => {
    setSettingsOpen(true);
  };
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [editName, setEditName] = useState<string>(segment.name || '');
  const [editPriority, setEditPriority] = useState<number>(segment.priority || 0);
  const [editEnabled, setEditEnabled] = useState<boolean>(!!segment.enabled);
  const [editRole, setEditRole] = useState<string>(segment.role || '');
  const [editDescription, setEditDescription] = useState<string>(segment.description || '');
  const [editCoverUrl, setEditCoverUrl] = useState<string>(segment.coverUrl || '');
  const [editType, setEditType] = useState<string>(segment.type || '');
  const [editMetadata, setEditMetadata] = useState<string>(
    segment.metadata ? JSON.stringify(segment.metadata, null, 2) : ''
  );

  const handleCloseSettings = () => {
    setSettingsOpen(false);
    setEditName(segment.name || '');
    setEditPriority(segment.priority || 0);
    setEditEnabled(!!segment.enabled);
    setEditRole(segment.role || '');
    setEditDescription(segment.description || '');
    setEditCoverUrl(segment.coverUrl || '');
    setEditType(segment.type || '');
    setEditMetadata(segment.metadata ? JSON.stringify(segment.metadata, null, 2) : '');
  };

  const handleSaveSettings = async () => {
    const key = endpoints.segmentor.list;
    setIsUpdating(true);

    // Validate metadata JSON if present
    let parsedMetadata: Record<string, any> | undefined = undefined;
    if (editMetadata && editMetadata.trim() !== '') {
      try {
        parsedMetadata = JSON.parse(editMetadata);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (err) {
        toast.error('Invalid metadata JSON');
        setIsUpdating(false);
        return;
      }
    }

    const payload: any = {
      name: editName,
      priority: editPriority,
      enabled: editEnabled,
      role: editRole || undefined,
      description: editDescription || undefined,
      coverUrl: editCoverUrl || undefined,
      type: editType || undefined,
    };

    if (parsedMetadata !== undefined) payload.metadata = parsedMetadata;

    // Build an updated list from cache and return it (simulate server 200)
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

    const updatedArray = currentArray.map((s: any) => (s.id === segment.id ? { ...s, ...payload } : s));

    const mutatePromise = mutate(
      key,
      async () => {
        await new Promise((r) => setTimeout(r, 300));
        return updatedArray;
      },
      { rollbackOnError: true }
    );

    try {
      toast.promise(mutatePromise, {
        loading: 'Saving...',
        success: 'Segment updated',
        error: 'Failed to save segment',
      });

      await mutatePromise;
      // Notify parent with updated segment when available
      try {
        const updatedSegment = updatedArray.find((s: any) => s.id === segment.id);
        if (updatedSegment) callParentUpdate(updatedSegment as ISegmentorCard);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (err) {
        /* ignore */
      }
      setSettingsOpen(false);
    } catch (err) {
      console.error('Failed to save segment settings', err);
    } finally {
      setIsUpdating(false);
    }
  };
  return (
    <Card sx={[{ textAlign: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]} {...other}>
      <Box sx={{ position: 'relative' }}>
        <IconButton
          aria-label="segment-settings"
          size="medium"
          onClick={handleOpenSettings}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 20,
            color: 'white',
            bgcolor: 'rgba(0,0,0,0.32)',
            width: 40,
            height: 40,
            padding: 0.5,
            '&:hover': { bgcolor: 'rgba(0,0,0,0.36)' },
          }}
        >
          <SvgIcon
          component={m.svg}
          animate={{ rotate: 360 }}
          transition={{ duration: 8, ease: 'linear', repeat: Infinity }}
        >
          {/* https://icon-sets.iconify.design/solar/settings-bold-duotone/ */}
          <path
            fill="currentColor"
            fillRule="evenodd"
            d="M14.279 2.152C13.909 2 13.439 2 12.5 2s-1.408 0-1.779.152a2.008 2.008 0 0 0-1.09 1.083c-.094.223-.13.484-.145.863a1.615 1.615 0 0 1-.796 1.353a1.64 1.64 0 0 1-1.579.008c-.338-.178-.583-.276-.825-.308a2.026 2.026 0 0 0-1.49.396c-.318.242-.553.646-1.022 1.453c-.47.807-.704 1.21-.757 1.605c-.07.526.074 1.058.4 1.479c.148.192.357.353.68.555c.477.297.783.803.783 1.361c0 .558-.306 1.064-.782 1.36c-.324.203-.533.364-.682.556a1.99 1.99 0 0 0-.399 1.479c.053.394.287.798.757 1.605c.47.807.704 1.21 1.022 1.453c.424.323.96.465 1.49.396c.242-.032.487-.13.825-.308a1.64 1.64 0 0 1 1.58.008c.486.28.774.795.795 1.353c.015.38.051.64.145.863c.204.49.596.88 1.09 1.083c.37.152.84.152 1.779.152s1.409 0 1.779-.152a2.008 2.008 0 0 0 1.09-1.083c.094-.223.13-.483.145-.863c.02-.558.309-1.074.796-1.353a1.64 1.64 0 0 1 1.579-.008c.338.178.583.276.825.308c.53.07 1.066-.073 1.49-.396c.318-.242.553-.646 1.022-1.453c.47-.807.704-1.21.757-1.605a1.99 1.99 0 0 0-.4-1.479c-.148-.192-.357-.353-.68-.555c-.477-.297-.783-.803-.783-1.361c0-.558.306-1.064.782-1.36c.324-.203.533-.364.682-.556a1.99 1.99 0 0 0 .399-1.479c-.053-.394-.287-.798-.757-1.605c-.47-.807-.704-1.21-1.022-1.453a2.026 2.026 0 0 0-1.49-.396c-.242.032-.487.13-.825.308a1.64 1.64 0 0 1-1.58-.008a1.615 1.615 0 0 1-.795-1.353c-.015-.38-.051-.64-.145-.863a2.007 2.007 0 0 0-1.09-1.083"
            clipRule="evenodd"
            opacity="0.5"
          />
          <path
            fill="currentColor"
            d="M15.523 12c0 1.657-1.354 3-3.023 3c-1.67 0-3.023-1.343-3.023-3S10.83 9 12.5 9c1.67 0 3.023 1.343 3.023 3"
          />
        </SvgIcon>
        </IconButton>
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
          src={segment.name}
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
          { label: 'Runs', value: 400 },
          { label: 'Success', value: 235 },
        ].map((stat) => (
          <Box key={stat.label} sx={{ gap: 0.5, display: 'flex', flexDirection: 'column' }}>
            <Box component="span" sx={{ typography: 'caption', color: 'text.secondary' }}>
              {stat.label}
            </Box>
            {fShortenNumber(stat.value)}
          </Box>
        ))}
      </Box>
      <Dialog open={settingsOpen} onClose={handleCloseSettings} fullWidth maxWidth="sm">
        <DialogTitle>Segment Settings</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            fullWidth
            label="Name"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
          />
          <TextField
            margin="dense"
            fullWidth
            type="number"
            label="Priority"
            value={editPriority}
            onChange={(e) => setEditPriority(Number(e.target.value))}
          />
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 1 }}>
            <FormControlLabel
              control={<Switch checked={editEnabled} onChange={(e) => setEditEnabled(e.target.checked)} />}
              label={editEnabled ? 'Enabled' : 'Disabled'}
            />
            <TextField
              margin="dense"
              label="Type"
              value={editType}
              onChange={(e) => setEditType(e.target.value)}
            />
            <TextField
              margin="dense"
              label="Role"
              value={editRole}
              onChange={(e) => setEditRole(e.target.value)}
            />
          </Box>

          <TextField
            margin="dense"
            fullWidth
            multiline
            minRows={2}
            label="Description"
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
          />

          <TextField
            margin="dense"
            fullWidth
            label="Cover URL"
            value={editCoverUrl}
            onChange={(e) => setEditCoverUrl(e.target.value)}
          />

          <TextField
            margin="dense"
            fullWidth
            multiline
            minRows={3}
            label="Metadata (JSON)"
            value={editMetadata}
            onChange={(e) => setEditMetadata(e.target.value)}
            placeholder='{"key": "value"}'
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSettings} variant="outlined" color="inherit">
            Cancel
          </Button>
          <Button onClick={handleSaveSettings} variant="contained" disabled={isUpdating}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}
