import { AccountLayout } from 'src/sections/customer/account-layout';

type LayoutProps = {
  children: React.ReactNode;
  params: { id: string };
};

const AccountLayoutWrapper = async ({ children, params }: LayoutProps) => {
  const { id } = params;
  return <AccountLayout customerId={id}>{children}</AccountLayout>;
};

export default AccountLayoutWrapper;
