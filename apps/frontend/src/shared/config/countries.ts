// START_MODULE_CONTRACT
//   PURPOSE: ISO 3166-1 alpha-2 country list with Russian names for the geo selector.
//   SCOPE: Static data; names from Intl.DisplayNames.
//   DEPENDS: none
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   COUNTRIES - sorted [{ code, name }]
// END_MODULE_MAP
const CODES = (
  'AD AE AF AG AI AL AM AO AR AT AU AW AZ BA BB BD BE BF BG BH BI BJ BM BN BO BR BS BT BW BY BZ CA CD CF CG CH CI ' +
  'CL CM CN CO CR CU CV CY CZ DE DJ DK DM DO DZ EC EE EG ER ES ET FI FJ FM FR GA GB GD GE GH GM GN GQ GR GT GW GY ' +
  'HK HN HR HT HU ID IE IL IN IQ IR IS IT JM JO JP KE KG KH KI KM KN KR KW KZ LA LB LC LI LK LR LS LT LU LV LY MA ' +
  'MC MD ME MG MH MK ML MM MN MO MR MT MU MV MW MX MY MZ NA NE NG NI NL NO NP NR NZ OM PA PE PG PH PK PL PR PS PT ' +
  'PW PY QA RO RS RU RW SA SB SC SD SE SG SI SK SL SM SN SO SR SS ST SV SY SZ TD TG TH TJ TL TM TN TO TR TT TV TW ' +
  'TZ UA UG US UY UZ VA VC VE VN VU WS XK YE ZA ZM ZW'
).split(' ')

const names = new Intl.DisplayNames(['ru'], { type: 'region' })

export const COUNTRIES = CODES.map((code) => ({ code, name: names.of(code) ?? code })).sort((a, b) =>
  a.name.localeCompare(b.name, 'ru'),
)
