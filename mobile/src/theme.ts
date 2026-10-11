/** SHUFFL Line-Up visual tokens. Cyan and amber are reserved for artwork/swipe semantics. */
export const colors = {
  bg: '#060609',
  surface: '#131318',
  raised: '#1B1B23',
  pink: '#FF2E7A',
  cyan: '#24E0FF',
  amber: '#FFC247',
  text: '#FBFAFF',
  muted: '#9C98AE',
  mutedDeep: '#6C6880',
  line: '#292831',
  border: 'rgba(255, 255, 255, 0.08)',
  borderStrong: 'rgba(255, 255, 255, 0.16)',
  pinkBorder: 'rgba(255, 46, 122, 0.35)',
  danger: '#FF5C6C',
  green: '#63E6A8',
  // Compatibility aliases used by existing screen components.
  mint: '#FF2E7A',
  purple: '#A57AFF',
  textSecondary: '#9C98AE',
  textMuted: '#6C6880',
} as const;

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 };
export const radius = { sm: 14, md: 20, lg: 28 };
