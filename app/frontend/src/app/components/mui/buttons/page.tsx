import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';

import { ButtonView } from 'src/sections/_examples/mui/button-view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Button | MUI - ${CONFIG.appName}` };

export default function Page() {
  return <ButtonView />;
}
