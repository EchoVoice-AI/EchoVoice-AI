import type { NavSectionProps } from 'src/components/nav-section';

import { paths } from 'src/routes/paths';

import { CONFIG } from 'src/global-config';

import { SvgColor } from 'src/components/svg-color';

// ----------------------------------------------------------------------

const icon = (name: string) => (
  <SvgColor src={`${CONFIG.assetsDir}/assets/icons/navbar/${name}.svg`} />
);

const ICONS = {
  job: icon('ic-job'),
  blog: icon('ic-blog'),
  chat: icon('ic-chat'),
  mail: icon('ic-mail'),
  user: icon('ic-user'),
  file: icon('ic-file'),
  lock: icon('ic-lock'),
  tour: icon('ic-tour'),
  order: icon('ic-order'),
  label: icon('ic-label'),
  blank: icon('ic-blank'),
  kanban: icon('ic-kanban'),
  folder: icon('ic-folder'),
  course: icon('ic-course'),
  banking: icon('ic-banking'),
  booking: icon('ic-booking'),
  invoice: icon('ic-invoice'),
  product: icon('ic-product'),
  calendar: icon('ic-calendar'),
  disabled: icon('ic-disabled'),
  external: icon('ic-external'),
  menuItem: icon('ic-menu-item'),
  ecommerce: icon('ic-ecommerce'),
  analytics: icon('ic-analytics'),
  dashboard: icon('ic-dashboard'),
  parameter: icon('ic-parameter'),
};

// ----------------------------------------------------------------------

export const navData: NavSectionProps['data'] = [
  /**
   * Overview
   */
  {
    subheader: 'Overview',
    items: [
      { title: 'Dashboard', path: paths.dashboard.root, icon: ICONS.dashboard },
      // { title: 'Ecommerce', path: paths.dashboard.general.ecommerce, icon: ICONS.ecommerce },
      // { title: 'Analytics', path: paths.dashboard.general.analytics, icon: ICONS.analytics },
      // { title: 'Banking', path: paths.dashboard.general.banking, icon: ICONS.banking },
      // { title: 'Booking', path: paths.dashboard.general.booking, icon: ICONS.booking },
      // { title: 'File', path: paths.dashboard.general.file, icon: ICONS.file },
      // { title: 'Course', path: paths.dashboard.general.course, icon: ICONS.course },
    ],
  },
  /**
   * Management
   */
  {
    subheader: 'Configurations',
    items: [
      {
        title: 'Segments',
        path: paths.dashboard.customer.root,
        icon: ICONS.user,
        children: [
          { title: 'Segments Overview', path: paths.dashboard.segments.root },
          { title: 'Segments List', path: paths.dashboard.segments.list },
        ],
      },
      {
        title: 'Retrievers',
        path: paths.dashboard.retrievers.root,
        icon: ICONS.user,
        children: [
          { title: 'Retrievers Overview', path: paths.dashboard.retrievers.root },
          { title: 'Retrievers Settings', path: paths.dashboard.retrievers.settings },
        ],
      },
    ],
  },
  {
    subheader: 'Policies',
    items: [
      {
        title: 'Safety',
        path: paths.dashboard.safety.root,
        icon: ICONS.user,
        children: [
          { title: 'Safety Policies', path: paths.dashboard.safety.root },
          { title: 'Safety Rules', path: paths.dashboard.safety.cards },
          { title: 'Safety List', path: paths.dashboard.safety.list },
          { title: 'Create Safety', path: paths.dashboard.safety.new },
          { title: 'Edit Safety', path: paths.dashboard.safety.demo.edit },
          { title: 'Safety Account', path: paths.dashboard.safety.account },
        ],
      },
      {
        title: 'Routing',
        path: paths.dashboard.routing.root,
        icon: ICONS.user,
        children: [
          { title: 'Routing Policies', path: paths.dashboard.routing.root },
          { title: 'Routing Rules', path: paths.dashboard.routing.cards },
          { title: 'Routing List', path: paths.dashboard.routing.list },
          { title: 'Create Routing', path: paths.dashboard.routing.new },
          { title: 'Edit Routing', path: paths.dashboard.routing.demo.edit },
          { title: 'Routing Account', path: paths.dashboard.routing.account },
        ],
      },
      {
        title: 'Generation',
        path: paths.dashboard.generation.root,
        icon: ICONS.user,
        children: [
          { title: 'Generation Overview', path: paths.dashboard.generation.root },
          { title: 'Generation Templates', path: paths.dashboard.generation.cards },
          { title: 'Generation List', path: paths.dashboard.generation.list },
          { title: 'Create Template', path: paths.dashboard.generation.new },
          { title: 'Edit Template', path: paths.dashboard.generation.demo.edit },
          { title: 'Generation Account', path: paths.dashboard.generation.account },
        ],
      },
    ],
  },
  {
    subheader: 'Integrations',
    items: [
      {
        title: 'Delivery',
        path: paths.dashboard.delivery.root,
        icon: ICONS.file,
        children: [
          { title: 'Delivery All', path: paths.dashboard.delivery.cards },
          { title: 'Delivery List', path: paths.dashboard.delivery.list },
        ],
      },
      {
        title: 'Offers',
        path: paths.dashboard.offers.root,
        icon: ICONS.user,
        children: [
          { title: 'Offers Overview', path: paths.dashboard.offers.root },
          { title: 'Offers List', path: paths.dashboard.offers.list },
        ],
      },
      {
        title: 'Data Sources',
        path: paths.dashboard.dataSources.root,
        icon: ICONS.user,
        children: [
          { title: 'Data Sources Overview', path: paths.dashboard.dataSources.root },
          { title: 'Data Sources Details', path: paths.dashboard.dataSources.details('1') },
        ],
      },
    ],
  },
];