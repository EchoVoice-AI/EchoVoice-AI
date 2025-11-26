import type { IPackageItem } from 'src/types/package';

import { z as zod } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import { Grid2 } from '@mui/material';
import Stack from '@mui/material/Stack';
import LoadingButton from '@mui/lab/LoadingButton';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { toast } from 'src/components/snackbar';
import { Form, Field } from 'src/components/hook-form';

// ----------------------------------------------------------------------

export const NewPackageSchema = zod.object({
  name: zod.string().min(1, 'Name is required'),
  type: zod.string().min(1, 'Type is required'),
  data_limit: zod.string().min(1, 'Data limit is required'),
  time_limit: zod.string().min(1, 'Time limit is required'),
  rate_limit: zod.string().min(1, 'Rate limit is required'),
  session_timeout: zod.number().min(1, 'Session timeout is required'),
  idle_timeout: zod.number().min(1, 'Idle timeout is required'),
  price: zod.string().min(1, 'Price is required'),
  status: zod.string(),
  validity_period: zod.string().min(1, 'Validity period is required'),
  features: zod.string().optional(),
  description: zod.string().optional(),
});

export type NewPackageSchemaType = zod.infer<typeof NewPackageSchema>;

// ----------------------------------------------------------------------

type Props = {
  currentPackage?: IPackageItem;
};

export function PackageNewEditForm({ currentPackage }: Props) {
  const router = useRouter();

  const methods = useForm<NewPackageSchemaType>({
    resolver: zodResolver(NewPackageSchema),
    defaultValues: {
      name: '',
      type: '',
      data_limit: '',
      time_limit: '',
      rate_limit: '',
      session_timeout: 0,
      idle_timeout: 0,      status: 'active',
      validity_period: '',
      features: '',
      description: '',
      ...currentPackage,
      price: currentPackage?.price !== undefined ? String(currentPackage.price) : '',
    },
  });

  const {
    reset,
    watch,
    control,
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const values = watch();

  const onSubmit = handleSubmit(async (data) => {
    try {
      await new Promise((res) => setTimeout(res, 500));
      toast.success(currentPackage ? 'Update success!' : 'Create success!');
      reset();
      router.push(paths.dashboard.package.list); // <- adjust route as needed
      console.info('Submitted data:', data);
    } catch (error) {
      console.error(error);
    }
  });

  return (
    <Form methods={methods} onSubmit={onSubmit}>
      <Grid2 container spacing={3}>
        <Grid2 size={{ xs: 12, md: 12 }}>
          <Card sx={{ p: 3 }}>
            <Box
              sx={{
                display: 'grid',
                rowGap: 3,
                columnGap: 2,
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
              <Field.Text name="validity_period" label="Validity Period" />
              <Field.Text name="price" label="Price" />
              <Field.Text name="features" label="Features (comma separated)" />
              <Field.Text name="description" label="Description" multiline rows={3} />
            </Box>

            <Stack sx={{ mt: 3, alignItems: 'flex-end' }}>
              <LoadingButton type="submit" variant="contained" loading={isSubmitting}>
                {currentPackage ? 'Save Changes' : 'Create Package'}
              </LoadingButton>
            </Stack>
          </Card>
        </Grid2>
      </Grid2>
    </Form>
  );
}
