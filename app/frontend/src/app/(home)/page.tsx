import type { Metadata } from 'next';

import { HomeView } from 'src/sections/home/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = {
  title: 'EchoVoice: Customer Personalization Orchestrator',
  keywords: [
    'EchoVoice',
    'Customer Personalization',
    'Personalization Orchestrator',
    'A/B/n experimentation',
    'regulated industries',
  ],
  description:
    'EchoVoice is a multi-agent AI personalization platform for regulated industries — delivering safe, on-brand, traceable customer messaging and A/B/n experimentation within an auditable orchestration pipeline.',
  openGraph: {
    title: 'EchoVoice: Customer Personalization Orchestrator',
    description:
      'EchoVoice delivers compliant, on-brand personalization and A/B/n experimentation for regulated domains via a coordinated, auditable multi-agent orchestration pipeline.',
    type: 'website',
    url: 'https://echovoice.ai',
    siteName: 'EchoVoice',
    images: [
      {
        url: 'https://echovoice.ai/og-image.png',
        width: 1200,
        height: 630,
        alt: 'EchoVoice: Customer Personalization Orchestrator',
      },
    ],
  },
  twitter: {
    title: 'EchoVoice: Customer Personalization Orchestrator',
    description:
      'EchoVoice: compliant, on-brand personalization and A/B/n experimentation in regulated industries — safe, traceable messaging orchestrated by specialized agents.',
    card: 'summary_large_image',
    images: [
      {
        url: 'https://echovoice.ai/og-image.png',
        width: 1200,
        height: 630,
        alt: 'EchoVoice: Customer Personalization Orchestrator',
      },
    ],
  },
};

export default function Page() {
  return <HomeView />;
}
