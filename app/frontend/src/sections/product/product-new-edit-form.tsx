import type { ILeaveItem } from 'src/types/product';

import { z as zod } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';
import LoadingButton from '@mui/lab/LoadingButton';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import {
  LEAVE_TYPE_OPTIONS,
} from 'src/_mock';
import { createProduct } from 'src/actions/product';

import { toast } from 'src/components/snackbar';
import { Form, Field, schemaHelper } from 'src/components/hook-form';

import { useAuthContext } from 'src/auth/hooks';

// ----------------------------------------------------------------------

export type NewLeaveSchemaType = zod.infer<typeof NewLeaveSchema>;

export const NewLeaveSchema = zod.object({
  leave_type: zod.string().min(1, { message: 'Leave type is required!' }),
  start_date: zod.string().nullable(),
  end_date: zod.string().nullable(),
  reason: schemaHelper
    .editor({ message: 'Description is required!' })
    .min(100, { message: 'Description must be at least 100 characters' })
    .max(500, { message: 'Description must be less than 500 characters' }),

});

// ----------------------------------------------------------------------

type Props = {
  currentLeave?: ILeaveItem;
};

export function LeaveNewEditForm({ currentLeave }: Props) {
  const router = useRouter();
  const { user } = useAuthContext()


  const defaultValues: NewLeaveSchemaType = {
    leave_type: '',
    start_date: null,
    end_date: null,
    reason: '',
  };

  const methods = useForm<NewLeaveSchemaType>({
    resolver: zodResolver(NewLeaveSchema),
    defaultValues: currentLeave ?? defaultValues,
  });

  const {
    reset,
    watch,
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const values = watch();

  const onSubmit = handleSubmit(async (data) => {
    const updatedData = {
      ...data,
      employee: user?.id,
      start_date: data.start_date ? data.start_date.split('T')[0] : null, // Ensure valid Date object
      end_date: data.end_date ? data.end_date.split('T')[0] : null, // Ensure valid Date object
    };

    try {
      const res = await createProduct(updatedData);
      console.info('RES', res);
      if (res.status) {
        console.info('RES', res);
        reset();
        toast.success(currentLeave ? 'Update success!' : 'Create success!');
        router.push(paths.dashboard.leave.root);
        console.info('DATA', updatedData);
      }
    } catch (error) {
      console.error(error);
    }
  });


  const renderDetails = () => (
    <Card>
      <CardHeader title="Details" subheader="Title, short description, image..." sx={{ mb: 3 }} />

      <Divider />

      <Stack spacing={3} sx={{ p: 3 }}>
        <Field.Select
          name="leave_type"
          label="Leave type"
          slotProps={{
            select: { native: true },
            inputLabel: { shrink: true },
          }}
        >
          {LEAVE_TYPE_OPTIONS.map((option) => (
            <option key={option.label} value={option.value}>
              {option.label}
            </option>
          ))}
        </Field.Select>


        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Duration</Typography>
          <Box
            sx={{
              rowGap: 3,
              columnGap: 2,
              display: 'grid',
              gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)' },
            }}
          >
            <Field.DatePicker name="start_date" label="From Date" />
            <Field.DatePicker name="end_date" label="End Date" />
          </Box>
        </Stack>

        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Reason</Typography>
          <Field.Editor name="reason" sx={{ maxHeight: 480 }} />
        </Stack>
      </Stack>
    </Card>
  );

  const renderActions = () => (
    <Box
      sx={{
        gap: 3,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
      }}
    >
      <LoadingButton type="submit" variant="contained" size="large" loading={isSubmitting}>
        {!currentLeave ? 'Create Application' : 'Save changes'}
      </LoadingButton>
    </Box>
  );

  return (
    <Form methods={methods} onSubmit={onSubmit}>
      <Stack spacing={{ xs: 3, md: 5 }} sx={{ mx: 'auto', maxWidth: { xs: 720, xl: 880 } }}>
        {renderDetails()}
        {renderActions()}
      </Stack>
    </Form>
  );
}
