import { _mock } from "./_mock";

export const _packages = Array.from({ length: 20 }, (_, index) => ({
  id: _mock.id(index),
  type: _mock.packageType(index),
  name: _mock.packageName(index),
  data_limit: _mock.dataLimit(index),
  time_limit: _mock.timeLimit(index),
  rate_limit: _mock.rateLimit(index),
  session_timeout: _mock.sessionTimeout(index),
  idle_timeout: _mock.idleTimeout(index),
  price: _mock.price(index),
  status: _mock.packageStatus(index),
  validity_period: _mock.validityPeriod(index),
  features: _mock.features(index),
  subscribers: _mock.number.subscribers(index),
  description: _mock.sentence(index),
  created_at: _mock.time(index),
  updated_at: _mock.time(index),
}));