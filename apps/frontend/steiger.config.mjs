import fsd from '@feature-sliced/steiger-plugin'
import { defineConfig } from 'steiger'

export default defineConfig([
  ...fsd.configs.recommended,
  {
    // Small app: slices are kept separate on purpose so each feature is independently replaceable.
    rules: { 'fsd/insignificant-slice': 'off' },
  },
])
