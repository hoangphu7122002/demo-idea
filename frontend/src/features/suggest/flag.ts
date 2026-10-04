/** Gate for the reader suggestion feature (unfinished work stays mergeable behind this). */
export const suggestEnabled = () => import.meta.env.VITE_FEATURE_SUGGEST === 'true'
