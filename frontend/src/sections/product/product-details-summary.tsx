import type { ILeaveItem2 } from 'src/types/product';

import { useForm } from 'react-hook-form';
import { useTabs } from 'minimal-shared/hooks';
import { varAlpha } from 'minimal-shared/utils';

import Tabs from '@mui/material/Tabs';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import { Box, Tab, Button, Rating } from '@mui/material';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { fNumber, fShortenNumber } from 'src/utils/format-number';

import { deleteProduct, updateProduct } from 'src/actions/product';

import { Form } from 'src/components/hook-form';
import { toast } from 'src/components/snackbar';
import { Iconify } from 'src/components/iconify';

import { ProductDetailsDescription } from './product-details-description';

// ----------------------------------------------------------------------

type Props = {
  product: ILeaveItem2;
  disableActions?: boolean;
  user: any;
};

export function ProductDetailsSummary({
  product,
  disableActions,
  user,
  ...other
}: Props) {
  const router = useRouter();

  const {
    id,
    employee,
    leave_days,
    leave_type,
    start_date,
    end_date,
    reason,
    status,
    applied_on,
    approved_by,

  } = product;

  const defaultValues = {
    id,
    employee,
    leave_days,
    leave_type,
    start_date,
    end_date,
    reason,
    status,
    applied_on,
    approved_by,
  };

  const methods = useForm<typeof defaultValues>({
    defaultValues,
  });

  const { handleSubmit } = methods;


  const onSubmit = handleSubmit(async (data) => {
    console.info('DATA', JSON.stringify(data, null, 2));

    try {

      const res = await deleteProduct(id);
      if (res.status) {
        router.push(paths.dashboard.leave.root);
        toast.success('Delete success!');
        router.push(paths.dashboard.leave.root);
      }
    } catch (error) {
      console.error(error);
    }
  });

  const handleAddCart = async (data: ILeaveItem2) => {
    try {
      const uploadData = {
        ...data,
        status: 'Approved',
        approved_by: user.id,
      };

      const res = await updateProduct(data.id, uploadData);
      if (res.status) {
        router.push(paths.dashboard.leave.root);
        toast.success('Approval success!');
        router.push(paths.dashboard.leave.root);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const renderPrice = () => (
    <Box sx={{ typography: 'h5' }}>
      {leave_days && (
        <Box
          component="span"
          sx={{ color: 'text.disabled', mr: 1.5 }}
        >
          Leave Days
        </Box>
      )}
      {fNumber(leave_days)}
    </Box>
  );

  const renderQuantity = () => (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, textAlign: 'center', alignItems: 'center' }}>
      <Typography variant="subtitle2" sx={{ flexGrow: 1, fontSize: 24 }}>
        Dates
      </Typography>

      <Stack spacing={1}>
        <Typography
          variant="caption"
          component="div"
          sx={{ textAlign: 'center', color: 'text.primary', fontWeight: 'fontWeightBold', fontSize: 16 }}
        >
          Start: {start_date}
        </Typography>

        <Typography
          variant="caption"
          component="div"
          sx={{ textAlign: 'center', color: 'text.primary', fontWeight: 'fontWeightBold', fontSize: 16 }}
        >
          End: {end_date}
        </Typography>
      </Stack>
    </Box>
  );

  const RenderActions = () => (
    <Box sx={{ gap: 2, display: 'flex' }}>
      <Button
        fullWidth
        disabled={disableActions}
        size="large"
        color="warning"
        variant="contained"
        startIcon={<Iconify icon="solar:verified-check-bold" width={24} />}
        onClick={() => handleAddCart(product)}
        sx={{ whiteSpace: 'nowrap' }}
      >
        Approve
      </Button>

      <Button fullWidth size="large" type="submit" variant="contained" color='error' >
        Delete
      </Button>
    </Box>
  );


  const renderRating = () => (
    <Box
      sx={{
        display: 'flex',
        typography: 'body2',
        alignItems: 'center',
        color: 'text.disabled',
      }}
    >
      <Rating size="small" value={leave_days} precision={0.1} readOnly sx={{ mr: 1 }} />
      {`(${fShortenNumber(leave_days)} Days)`}
    </Box>
  );

  const RenderLabels = () => {
    const tabs = useTabs('description');

    return (
      <Card>
        <Tabs
          value={tabs.value}
          onChange={tabs.onChange}
          sx={[
            (theme) => ({
              px: 3,
              boxShadow: `inset 0 -2px 0 0 ${varAlpha(theme.vars.palette.grey['500Channel'], 0.08)}`,
            }),
          ]}
        >
          {[
            { value: 'description', label: 'Description' },
            // { value: 'reviews', label: `Reviews (${product?.reviews.length})` },
          ].map((tab) => (
            <Tab key={tab.value} value={tab.value} label={tab.label} />
          ))}
        </Tabs>

        {tabs.value === 'description' && (
          <ProductDetailsDescription description={product?.reason ?? ''} />
        )}
      </Card>
    );
  };

  return (
    <Form methods={methods} onSubmit={onSubmit}>
      <Stack spacing={3} sx={{ pt: 3 }} {...other} >
        <Stack spacing={2} alignItems="center">
          <Typography variant="h5">{employee}</Typography>
          {renderRating()}
          {renderPrice()}
        </Stack>

        <Divider sx={{ borderStyle: 'dashed' }} />

        {renderQuantity()}
        <Box
          sx={{
            gap: 5,
            my: 10,
            display: 'grid',
            gridTemplateColumns: { xs: 'repeat(1, 1fr)', md: 'repeat(1, 1fr)' },
          }}
        >
          <Box sx={{ textAlign: 'center', px: 5 }}>
            {status === 'Approved' ? (
              <Iconify icon="solar:verified-check-bold" width={32} sx={{ color: 'success.main' }} />
            ) : (
              <Iconify icon="solar:user-cross-bold" width={32} sx={{ color: 'error.main' }} />
            )}

            <Typography variant="subtitle1" sx={{ mb: 1, mt: 2 }}>
              Leave Status
            </Typography>

            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {status}
            </Typography>
          </Box>
        </Box>
        <RenderLabels />

        <Divider sx={{ borderStyle: 'dashed' }} />

        <RenderActions />
      </Stack>
    </Form>
  );
}
