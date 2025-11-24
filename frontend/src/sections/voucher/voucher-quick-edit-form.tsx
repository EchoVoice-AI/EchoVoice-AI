import type { IPackageItem } from 'src/types/package';

import { z as zod } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import LoadingButton from '@mui/lab/LoadingButton';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';

import { toast } from 'src/components/snackbar';
import { Form, Field } from 'src/components/hook-form';

// ----------------------------------------------------------------------

export type PackageQuickEditSchemaType = zod.infer<typeof PackageQuickEditSchema>;

export const PackageQuickEditSchema = zod.object({
  name: zod.string().min(1, { message: 'Name is required!' }),
  type: zod.string().min(1, { message: 'Type is required!' }),
  data_limit: zod.string(),
  time_limit: zod.string(),
  rate_limit: zod.string(),
  session_timeout: zod.coerce.number().min(0, { message: 'Session timeout must be positive' }),
  idle_timeout: zod.coerce.number().min(0, { message: 'Idle timeout must be positive' }),
  price: zod.coerce.number().min(0, { message: 'Price must be positive' }),
  status: zod.string(),
  validity_period: zod.string(),
  features: zod.string(),
  subscribers: zod.coerce.number(),
  description: zod.string(),
});


// ----------------------------------------------------------------------

type Props = {
  open: boolean;
  onClose: () => void;
  currentPackage?: IPackageItem;
};

export function PackageQuickEditForm({ currentPackage, open, onClose }: Props) {
  const defaultValues: PackageQuickEditSchemaType = {
  name: '',
  type: '',
  data_limit: '',
  time_limit: '',
  rate_limit: '',
  session_timeout: 0,
  idle_timeout: 0,
  price: 0,
  status: 'active',
  validity_period: '',
  features: '',
  subscribers: 0,
  description: '',
};

  const methods = useForm<PackageQuickEditSchemaType>({
    mode: 'all',
    resolver: zodResolver(PackageQuickEditSchema),
    defaultValues,
    values: currentPackage,
  });

  const {
    reset,
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const onSubmit = handleSubmit(async (data) => {
    const promise = new Promise((resolve) => setTimeout(resolve, 1000));

    try {
      reset();
      onClose();

      toast.promise(promise, {
        loading: 'Loading...',
        success: 'Update success!',
        error: 'Update error!',
      });

      await promise;

      console.info('DATA', data);
    } catch (error) {
      console.error(error);
    }
  });

  return (
    <Dialog fullWidth open={open} onClose={onClose} PaperProps={{ sx: { maxWidth: 720 } }}>
      <DialogTitle>Edit Package</DialogTitle>

      <Form methods={methods} onSubmit={onSubmit}>
        <DialogContent>
          <Box
            sx={{
              rowGap: 3,
              columnGap: 2,
              display: 'grid',
              gridTemplateColumns: { xs: 'repeat(1, 1fr)', sm: 'repeat(2, 1fr)' },
            }}
          >
            <Field.Text name="name" label="Package Name" />
            <Field.Text name="type" label="Type" />
            <Field.Text name="data_limit" label="Data Limit" />
            <Field.Text name="time_limit" label="Time Limit" />
            <Field.Text name="rate_limit" label="Rate Limit" />
            <Field.Text name="session_timeout" label="Session Timeout" />
            <Field.Text name="idle_timeout" label="Idle Timeout" />
            <Field.Text name="price" label="Price" type="number" />
            <Field.Text name="status" label="Status" />
            <Field.Text name="validity_period" label="Validity Period" />
            <Field.Text name="features" label="Features" />
            <Field.Text name="subscribers" label="Subscribers" type="number" />
            <Field.Text name="description" label="Description" multiline rows={3} />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button variant="outlined" onClick={onClose}>Cancel</Button>
          <LoadingButton type="submit" variant="contained" loading={isSubmitting}>
            Save
          </LoadingButton>
        </DialogActions>
      </Form>
    </Dialog>
  );
}
