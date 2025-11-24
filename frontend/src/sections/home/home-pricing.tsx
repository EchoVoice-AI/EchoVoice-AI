import type { BoxProps } from '@mui/material/Box';

import { m } from 'framer-motion';
import { useTabs } from 'minimal-shared/hooks';
import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

import { paths } from 'src/routes/paths';

import { CONFIG } from 'src/global-config';

import { Iconify } from 'src/components/iconify';
import { varFade, varScale, MotionViewport } from 'src/components/animate';

import { SectionTitle } from './components/section-title';
import { FloatLine, FloatXIcon } from './components/svg-elements';

// ----------------------------------------------------------------------

export function HomePricing({ sx, ...other }: BoxProps) {
  const tabs = useTabs('Standard');

  const renderDescription = () => (
    <SectionTitle
      caption="Plans"
      title="Transparent"
      txtGradient="Pricing"
      description="Pick a plan that fits your team: from quick pilots to enterprise-grade orchestration with audit controls and SLA-backed support."
      sx={{ mb: 8, textAlign: 'center' }}
    />
  );

  const renderContentDesktop = () => (
    <Box gridTemplateColumns="repeat(3, 1fr)" sx={{ display: { xs: 'none', md: 'grid' } }}>
      {PLANS.map((plan) => (
        <PlanCard
          key={plan.license}
          plan={plan}
          sx={(theme) => ({
            ...(plan.license === 'Plus' && {
              [theme.breakpoints.down(1440)]: {
                borderLeft: `dashed 1px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.2)}`,
                borderRight: `dashed 1px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.2)}`,
              },
            }),
          })}
        />
      ))}
    </Box>
  );

  const renderContentMobile = () => (
    <Stack spacing={5} alignItems="center" sx={{ display: { md: 'none' } }}>
      <Tabs
        value={tabs.value}
        onChange={tabs.onChange}
        sx={[
          (theme) => ({
            boxShadow: `0px -2px 0px 0px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.08)} inset`,
          }),
        ]}
      >
        {PLANS.map((tab) => (
          <Tab key={tab.license} value={tab.license} label={tab.license} />
        ))}
      </Tabs>

      <Box
        sx={[
          (theme) => ({
            width: 1,
            borderRadius: 2,
            border: `dashed 1px ${varAlpha(theme.vars.palette.grey['500Channel'], 0.2)}`,
          }),
        ]}
      >
        {PLANS.map(
          (tab) => tab.license === tabs.value && <PlanCard key={tab.license} plan={tab} />
        )}
      </Box>
    </Stack>
  );

  return (
    <Box
      component="section"
      sx={[{ py: 10, position: 'relative' }, ...(Array.isArray(sx) ? sx : [sx])]}
      {...other}
    >
      <MotionViewport>
        <FloatLine vertical sx={{ top: 0, left: 80 }} />

        <Container>{renderDescription()}</Container>

        <Box
          sx={(theme) => ({
            position: 'relative',
            '&::before, &::after': {
              width: 64,
              height: 64,
              content: "''",
              [theme.breakpoints.up(1440)]: { display: 'block' },
            },
          })}
        >
          <Container>{renderContentDesktop()}</Container>

          <FloatLine sx={{ top: 64, left: 0 }} />
          <FloatLine sx={{ bottom: 64, left: 0 }} />
        </Box>

        <Container>{renderContentMobile()}</Container>
      </MotionViewport>
    </Box>
  );
}

// ----------------------------------------------------------------------

type PlanCardProps = BoxProps & {
  plan: {
    license: string;
    price: number;
    commons: string[];
    options: string[];
    icons: string[];
  };
};

const renderLines = () => (
  <>
    <FloatLine vertical sx={{ top: -64, left: 0, height: 'calc(100% + (64px * 2))' }} />
    <FloatLine vertical sx={{ top: -64, right: 0, height: 'calc(100% + (64px * 2))' }} />
    <FloatXIcon sx={{ top: -8, left: -8 }} />
    <FloatXIcon sx={{ top: -8, right: -8 }} />
    <FloatXIcon sx={{ bottom: -8, left: -8 }} />
    <FloatXIcon sx={{ bottom: -8, right: -8 }} />
  </>
);

function PlanCard({ plan, sx, ...other }: PlanCardProps) {
  return (
    <MotionViewport>
      <Box
        sx={[
          () => ({
            px: 6,
            py: 8,
            gap: 5,
            display: 'flex',
            position: 'relative',
            flexDirection: 'column',
          }),
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
        {...other}
      >
        {plan.license === 'Plus' && renderLines()}

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Stack flexGrow={1}>
            <m.div variants={varFade('inLeft', { distance: 24 })}>
              <Typography variant="h4" component="h6">
                {plan.license}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                {plan.license}
              </Typography>
            </m.div>

            <m.div variants={varScale('inX')}>
              <Box
                sx={{
                  width: 32,
                  height: 6,
                  opacity: 0.24,
                  borderRadius: 1,
                  bgcolor: 'error.main',
                  ...(plan.license === 'Standard' && { bgcolor: 'primary.main' }),
                  ...(plan.license === 'Plus'&& { bgcolor: 'secondary.main' }),
                }}
              />
            </m.div>
          </Stack>

          <m.div variants={varFade('inLeft', { distance: 24 })}>
            <Box component="span" sx={{ typography: 'h3' }}>
              KES {plan.price.toLocaleString()}
              <Box component="span" sx={{ typography: 'body1', color: 'text.secondary' }}>
                /month
              </Box>
            </Box>
          </m.div>
        </Box>

        <Box sx={{ gap: 2, display: 'flex' }}>
          {plan.icons.map((icon, index) => (
            <Box
              component={m.img}
              variants={varFade('in')}
              key={icon}
              alt={icon}
              src={icon}
              sx={{
                width: 24,
                height: 24,
                ...(plan.license === 'Standard' && [1, 2].includes(index) && { display: 'none' }),
              }}
            />
          ))}
          {plan.license === 'Standard' && (
            <Box component={m.span} variants={varFade('in')} sx={{ ml: -1 }}>
              (only)
            </Box>
          )}
        </Box>

        <Stack spacing={2.5}>
          {plan.commons.map((option) => (
            <Box
              key={option}
              component={m.div}
              variants={varFade('in')}
              sx={{
                gap: 1.5,
                display: 'flex',
                typography: 'body2',
                alignItems: 'center',
              }}
            >
              <Iconify width={16} icon="eva:checkmark-fill" />
              {option}
            </Box>
          ))}

          <m.div variants={varFade('inLeft', { distance: 24 })}>
            <Divider sx={{ borderStyle: 'dashed' }} />
          </m.div>

          {plan.options.map((option, index) => {
            const disabled =
              (plan.license === 'Standard' && [1, 2, 3].includes(index)) ||
              (plan.license === 'Plus' && [3].includes(index));

            return (
              <Box
                key={option}
                component={m.div}
                variants={varFade('in')}
                sx={{
                  gap: 1.5,
                  display: 'flex',
                  typography: 'body2',
                  alignItems: 'center',
                  ...(disabled && { color: 'text.disabled', textDecoration: 'line-through' }),
                }}
              >
                <Iconify
                  width={18}
                  icon={disabled ? 'mingcute:close-line' : 'eva:checkmark-fill'}
                />
                {option}
              </Box>
            );
          })}
        </Stack>

        <m.div variants={varFade('inUp', { distance: 24 })}>
          <Button
            fullWidth
            variant={plan.license === 'Premium' ? 'contained' : 'outlined'}
            color="primary"
            size="large"
            target="_blank"
            rel="noopener"
            href={paths.minimalStore}
          >
            Subscribe Now
          </Button>
        </m.div>
      </Box>
    </MotionViewport>
  );
}

// ----------------------------------------------------------------------

const PLANS = Array.from({ length: 3 }, (_, index) => ({
  license: ['Starter', 'Pro', 'Enterprise'][index],
  price: [49, 199, 999][index],
  commons: [
    'Compliance-first defaults',
    'A/B/n experiment support',
    'Audit logs & traceability',
    'Role-based access control',
  ],
  options: [
    'Email support',
    'Priority support',
    'Dedicated account manager',
    'Custom SLAs',
  ],
  icons: [
    `${CONFIG.assetsDir}/assets/icons/platforms/ic-wifi.svg`,
    `${CONFIG.assetsDir}/assets/icons/platforms/ic-speed.svg`,
    `${CONFIG.assetsDir}/assets/icons/platforms/ic-support.svg`,
  ],
}));
