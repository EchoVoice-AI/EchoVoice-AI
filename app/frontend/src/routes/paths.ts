import { kebabCase } from 'es-toolkit';

import { _id, _postTitles } from 'src/_mock/assets';

// ----------------------------------------------------------------------

const MOCK_ID = _id[1];

const MOCK_TITLE = _postTitles[2];

const ROOTS = {
  AUTH: '/auth',
  AUTH_DEMO: '/auth-demo',
  DASHBOARD: '/dashboard',
};

// ----------------------------------------------------------------------

export const paths = {
  comingSoon: '/coming-soon',
  maintenance: '/maintenance',
  pricing: '/pricing',
  payment: '/payment',
  about: '/about-us',
  contact: '/contact-us',
  faqs: '/faqs',
  page403: '/error/403',
  page404: '/error/404',
  page500: '/error/500',
  components: '/components',
  docs: 'https://docs.minimals.cc',
  changelog: 'https://docs.minimals.cc/changelog',
  zoneStore: 'https://mui.com/store/items/zone-landing-page/',
  minimalStore: 'https://mui.com/store/items/minimal-dashboard/',
  freeUI: 'https://mui.com/store/items/minimal-dashboard-free/',
  figmaUrl: 'https://www.figma.com/design/cAPz4pYPtQEXivqe11EcDE/%5BPreview%5D-Minimal-Web.v6.0.0',
  leave: {
    root: `/leave`,
    checkout: `/leave/checkout`,
    details: (id: string) => `/leave/${id}`,
    demo: { details: `/leave/${MOCK_ID}` },
  },
  post: {
    root: `/post`,
    details: (title: string) => `/post/${kebabCase(title)}`,
    demo: { details: `/post/${kebabCase(MOCK_TITLE)}` },
  },
  // AUTH
  auth: {
    amplify: {
      signIn: `${ROOTS.AUTH}/amplify/sign-in`,
      verify: `${ROOTS.AUTH}/amplify/verify`,
      signUp: `${ROOTS.AUTH}/amplify/sign-up`,
      updatePassword: `${ROOTS.AUTH}/amplify/update-password`,
      resetPassword: `${ROOTS.AUTH}/amplify/reset-password`,
    },
    jwt: { signIn: `${ROOTS.AUTH}/jwt/sign-in`, signUp: `${ROOTS.AUTH}/jwt/sign-up` },
    firebase: {
      signIn: `${ROOTS.AUTH}/firebase/sign-in`,
      verify: `${ROOTS.AUTH}/firebase/verify`,
      signUp: `${ROOTS.AUTH}/firebase/sign-up`,
      resetPassword: `${ROOTS.AUTH}/firebase/reset-password`,
    },
    auth0: { signIn: `${ROOTS.AUTH}/auth0/sign-in` },
    supabase: {
      signIn: `${ROOTS.AUTH}/supabase/sign-in`,
      verify: `${ROOTS.AUTH}/supabase/verify`,
      signUp: `${ROOTS.AUTH}/supabase/sign-up`,
      updatePassword: `${ROOTS.AUTH}/supabase/update-password`,
      resetPassword: `${ROOTS.AUTH}/supabase/reset-password`,
    },
  },
  authDemo: {
    split: {
      signIn: `${ROOTS.AUTH_DEMO}/split/sign-in`,
      signUp: `${ROOTS.AUTH_DEMO}/split/sign-up`,
      resetPassword: `${ROOTS.AUTH_DEMO}/split/reset-password`,
      updatePassword: `${ROOTS.AUTH_DEMO}/split/update-password`,
      verify: `${ROOTS.AUTH_DEMO}/split/verify`,
    },
    centered: {
      signIn: `${ROOTS.AUTH_DEMO}/centered/sign-in`,
      signUp: `${ROOTS.AUTH_DEMO}/centered/sign-up`,
      resetPassword: `${ROOTS.AUTH_DEMO}/centered/reset-password`,
      updatePassword: `${ROOTS.AUTH_DEMO}/centered/update-password`,
      verify: `${ROOTS.AUTH_DEMO}/centered/verify`,
    },
  },
  // DASHBOARD
  dashboard: {
    root: ROOTS.DASHBOARD,
    mail: `${ROOTS.DASHBOARD}/mail`,
    chat: `${ROOTS.DASHBOARD}/chat`,
    blank: `${ROOTS.DASHBOARD}/blank`,
    kanban: `${ROOTS.DASHBOARD}/kanban`,
    calendar: `${ROOTS.DASHBOARD}/calendar`,
    fileManager: `${ROOTS.DASHBOARD}/file-manager`,
    permission: `${ROOTS.DASHBOARD}/permission`,
    general: {
      app: `${ROOTS.DASHBOARD}/app`,
      ecommerce: `${ROOTS.DASHBOARD}/ecommerce`,
      analytics: `${ROOTS.DASHBOARD}/analytics`,
      banking: `${ROOTS.DASHBOARD}/banking`,
      booking: `${ROOTS.DASHBOARD}/booking`,
      file: `${ROOTS.DASHBOARD}/file`,
      course: `${ROOTS.DASHBOARD}/course`,
    },
    user: {
      root: `${ROOTS.DASHBOARD}/user`,
      new: `${ROOTS.DASHBOARD}/user/new`,
      list: `${ROOTS.DASHBOARD}/user/list`,
      cards: `${ROOTS.DASHBOARD}/user/cards`,
      profile: `${ROOTS.DASHBOARD}/user/profile`,
      account: `${ROOTS.DASHBOARD}/user/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/user/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/user/${MOCK_ID}/edit` },
    },
    customer: {
      root: `${ROOTS.DASHBOARD}/customer`,
      new: `${ROOTS.DASHBOARD}/customer/new`,
      list: `${ROOTS.DASHBOARD}/customer/list`,
      cards: `${ROOTS.DASHBOARD}/customer/cards`,
      profile: `${ROOTS.DASHBOARD}/customer/profile`,
      account: `${ROOTS.DASHBOARD}/customer/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/customer/${id}/edit`,
      edit2: (id: string) => `${ROOTS.DASHBOARD}/customer/${id}/account`,
      demo: { edit: `${ROOTS.DASHBOARD}/customer/${MOCK_ID}/edit` },
    },
    package: {
      root: `${ROOTS.DASHBOARD}/package`,
      new: `${ROOTS.DASHBOARD}/package/new`,
      list: `${ROOTS.DASHBOARD}/package/list`,
      cards: `${ROOTS.DASHBOARD}/package/cards`,
      profile: `${ROOTS.DASHBOARD}/package/profile`,
      account: `${ROOTS.DASHBOARD}/package/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/package/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/package/${MOCK_ID}/edit` },
    },
    generation: {
      root: `${ROOTS.DASHBOARD}/generation`,
      new: `${ROOTS.DASHBOARD}/generation/new`,
      list: `${ROOTS.DASHBOARD}/generation/list`,
      cards: `${ROOTS.DASHBOARD}/generation/cards`,
      profile: `${ROOTS.DASHBOARD}/generation/profile`,
      account: `${ROOTS.DASHBOARD}/generation/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/generation/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/generation/${MOCK_ID}/edit` },
    },
    voucher: {
      root: `${ROOTS.DASHBOARD}/voucher`,
      new: `${ROOTS.DASHBOARD}/voucher/new`,
      list: `${ROOTS.DASHBOARD}/voucher/list`,
      cards: `${ROOTS.DASHBOARD}/voucher/cards`,
      profile: `${ROOTS.DASHBOARD}/voucher/profile`,
      account: `${ROOTS.DASHBOARD}/voucher/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/voucher/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/voucher/${MOCK_ID}/edit` },
    },
    delivery: {
      root: `${ROOTS.DASHBOARD}/delivery`,
      new: `${ROOTS.DASHBOARD}/delivery/new`,
      list: `${ROOTS.DASHBOARD}/delivery/list`,
      cards: `${ROOTS.DASHBOARD}/delivery/cards`,
      profile: `${ROOTS.DASHBOARD}/delivery/profile`,
      account: `${ROOTS.DASHBOARD}/delivery/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/delivery/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/delivery/${MOCK_ID}/edit` },
    },
    equipment: {
      root: `${ROOTS.DASHBOARD}/equipment`,
      new: `${ROOTS.DASHBOARD}/equipment/new`,
      list: `${ROOTS.DASHBOARD}/equipment/list`,
      cards: `${ROOTS.DASHBOARD}/equipment/cards`,
      profile: `${ROOTS.DASHBOARD}/equipment/profile`,
      account: `${ROOTS.DASHBOARD}/equipment/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/equipment/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/equipment/${MOCK_ID}/edit` },
    },
    // Custom backend-aligned sections
    segments: {
      root: `${ROOTS.DASHBOARD}/segments`,
      new: `${ROOTS.DASHBOARD}/segments/new`,
      list: `${ROOTS.DASHBOARD}/segments/list`,
      cards: `${ROOTS.DASHBOARD}/segments/cards`,
      profile: `${ROOTS.DASHBOARD}/segments/profile`,
      account: `${ROOTS.DASHBOARD}/segments/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/segments/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/segments/${MOCK_ID}/edit` },
    },
    offers: {
      root: `${ROOTS.DASHBOARD}/offers`,
      new: `${ROOTS.DASHBOARD}/offers/new`,
      list: `${ROOTS.DASHBOARD}/offers/list`,
      cards: `${ROOTS.DASHBOARD}/offers/cards`,
      profile: `${ROOTS.DASHBOARD}/offers/profile`,
      account: `${ROOTS.DASHBOARD}/offers/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/offers/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/offers/${MOCK_ID}/edit` },
    },
    retrievers: {
      root: `${ROOTS.DASHBOARD}/retrievers`,
      settings: `${ROOTS.DASHBOARD}/retrievers/settings`,
    },
    safety: {
      root: `${ROOTS.DASHBOARD}/safety`,
      new: `${ROOTS.DASHBOARD}/safety/new`,
      list: `${ROOTS.DASHBOARD}/safety/list`,
      cards: `${ROOTS.DASHBOARD}/safety/cards`,
      profile: `${ROOTS.DASHBOARD}/safety/profile`,
      account: `${ROOTS.DASHBOARD}/safety/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/safety/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/safety/${MOCK_ID}/edit` },
    },
    routing: {
      root: `${ROOTS.DASHBOARD}/routing`,
      new: `${ROOTS.DASHBOARD}/routing/new`,
      list: `${ROOTS.DASHBOARD}/routing/list`,
      cards: `${ROOTS.DASHBOARD}/routing/cards`,
      profile: `${ROOTS.DASHBOARD}/routing/profile`,
      account: `${ROOTS.DASHBOARD}/routing/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/routing/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/routing/${MOCK_ID}/edit` },
    },
    payment: {
      root: `${ROOTS.DASHBOARD}/payment`,
      new: `${ROOTS.DASHBOARD}/payment/new`,
      list: `${ROOTS.DASHBOARD}/payment/list`,
      cards: `${ROOTS.DASHBOARD}/payment/cards`,
      profile: `${ROOTS.DASHBOARD}/payment/profile`,
      account: `${ROOTS.DASHBOARD}/payment/account`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/payment/${id}/edit`,
      demo: { edit: `${ROOTS.DASHBOARD}/payment/${MOCK_ID}/edit` },
    },
    leave: {
      root: `${ROOTS.DASHBOARD}/leave`,
      new: `${ROOTS.DASHBOARD}/leave/new`,
      details: (id: string) => `${ROOTS.DASHBOARD}/leave/${id}`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/leave/${id}/edit`,
      balances: `${ROOTS.DASHBOARD}/leave/balances`,
      demo: {
        details: `${ROOTS.DASHBOARD}/leave/${MOCK_ID}`,
        edit: `${ROOTS.DASHBOARD}/leave/${MOCK_ID}/edit`,
      },
    },
    invoice: {
      root: `${ROOTS.DASHBOARD}/invoice`,
      new: `${ROOTS.DASHBOARD}/invoice/new`,
      details: (id: string) => `${ROOTS.DASHBOARD}/invoice/${id}`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/invoice/${id}/edit`,
      demo: {
        details: `${ROOTS.DASHBOARD}/invoice/${MOCK_ID}`,
        edit: `${ROOTS.DASHBOARD}/invoice/${MOCK_ID}/edit`,
      },
    },
    post: {
      root: `${ROOTS.DASHBOARD}/post`,
      new: `${ROOTS.DASHBOARD}/post/new`,
      details: (title: string) => `${ROOTS.DASHBOARD}/post/${kebabCase(title)}`,
      edit: (title: string) => `${ROOTS.DASHBOARD}/post/${kebabCase(title)}/edit`,
      demo: {
        details: `${ROOTS.DASHBOARD}/post/${kebabCase(MOCK_TITLE)}`,
        edit: `${ROOTS.DASHBOARD}/post/${kebabCase(MOCK_TITLE)}/edit`,
      },
    },
    order: {
      root: `${ROOTS.DASHBOARD}/order`,
      details: (id: string) => `${ROOTS.DASHBOARD}/order/${id}`,
      demo: { details: `${ROOTS.DASHBOARD}/order/${MOCK_ID}` },
    },
    job: {
      root: `${ROOTS.DASHBOARD}/job`,
      new: `${ROOTS.DASHBOARD}/job/new`,
      details: (id: string) => `${ROOTS.DASHBOARD}/job/${id}`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/job/${id}/edit`,
      demo: {
        details: `${ROOTS.DASHBOARD}/job/${MOCK_ID}`,
        edit: `${ROOTS.DASHBOARD}/job/${MOCK_ID}/edit`,
      },
    },
    tour: {
      root: `${ROOTS.DASHBOARD}/tour`,
      new: `${ROOTS.DASHBOARD}/tour/new`,
      details: (id: string) => `${ROOTS.DASHBOARD}/tour/${id}`,
      edit: (id: string) => `${ROOTS.DASHBOARD}/tour/${id}/edit`,
      demo: {
        details: `${ROOTS.DASHBOARD}/tour/${MOCK_ID}`,
        edit: `${ROOTS.DASHBOARD}/tour/${MOCK_ID}/edit`,
      },
    },
    dataSources: {
    root: `${ROOTS.DASHBOARD}/data-sources`,
    details: (id: string) => `${ROOTS.DASHBOARD}/data-sources/${id}`,
  },
  },
  

  // product
  product: {
    root: '/product',
    demo: { details: '/product/1' },
    checkout: '/product/checkout',
  },
};
