
import type { ICustomerItem } from 'src/types/customer';

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

import { useCustomerStore } from 'src/store/customerStore';

import { toast } from 'src/components/snackbar';
import { Form, Field } from 'src/components/hook-form';

// ----------------------------------------------------------------------

export type CustomerQuickEditSchemaType = zod.infer<typeof CustomerQuickEditSchema>;

type Props = {
  currentCustomer: ICustomerItem;
  open: boolean;
  onClose: () => void;
};

export const CustomerQuickEditSchema = zod.object({
  id: zod.string().optional(),
  name: zod.string().min(1, { message: 'Name is required!' }),
  city: zod.string().optional(),
  role: zod.string().optional(),
  email: zod.string().min(1, { message: 'Email is required!' }),
  state: zod.string().optional(),
  status: zod.string().optional(),
  address: zod.string().min(1, { message: 'Address is required!' }),
  country: zod.string().optional(),
  zipCode: zod.string().optional(),
  service_type: zod.string().min(1, { message: 'Service type is required!' }),
  avatarUrl: zod.string().optional(),
  phoneNumber: zod.string().min(1, { message: 'Phone number is required!' }),
  isVerified: zod.boolean().optional(),
});

export function CustomerQuickEditForm({ currentCustomer, open, onClose }: Props) {
  const editCustomer = useCustomerStore((state) => state.editCustomer);
  const defaultValues: CustomerQuickEditSchemaType = {
    id: '',
    name: '',
    city: '',
    role: '',
    email: '',
    state: '',
    status: '',
    address: '',
    country: '',
    zipCode: '',
    service_type: '',
    avatarUrl: '',
    phoneNumber: '',
    isVerified: false,
  };

  const methods = useForm<CustomerQuickEditSchemaType>({
    mode: 'all',
    resolver: zodResolver(CustomerQuickEditSchema),
    defaultValues,
    values: currentCustomer,
  });

  const {
    reset,
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const onSubmit = handleSubmit(async (data) => {
    try {
      toast.promise(
        editCustomer({ ...currentCustomer, ...data }),
        {
          loading: 'Updating customer...',
          success: 'Update success!',
          error: 'Update error!'
        }
      );
      await editCustomer({ ...currentCustomer, ...data });
      reset();
      onClose();
    } catch (error) {
      console.error(error);
    }
  });

  return (
    <Dialog fullWidth open={open} onClose={onClose} PaperProps={{ sx: { maxWidth: 720 } }}>
      <DialogTitle>Edit Customer</DialogTitle>

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
            <Field.Text name="name" label="Name" />
            <Field.Text name="email" label="Email" />
            <Field.Text name="phoneNumber" label="Phone Number" />
            <Field.Text name="service_type" label="Service Type" />
            <Field.Text name="address" label="Address" />
            <Field.Text name="city" label="City" />
            <Field.Text name="state" label="State" />
            <Field.Text name="country" label="Country" />
            <Field.Text name="zipCode" label="Zip Code" />
            <Field.Text name="role" label="Role" />
            <Field.Text name="status" label="Status" />
            <Field.Text name="avatarUrl" label="Avatar URL" />
            <Field.Checkbox name="isVerified" label="Is Verified" />
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
