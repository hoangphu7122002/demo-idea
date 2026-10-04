import { api } from '../../api/client'
import type { components } from '../../api/schema'
import { baseApi, fromApi } from '../../services/baseApi'

export type Suggestion = components['schemas']['SuggestionOut']
export type SuggestionIn = components['schemas']['SuggestionIn']

export const suggestApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    submitSuggestion: build.mutation<Suggestion, { slug: string; body: SuggestionIn }>({
      queryFn: ({ slug, body }) => fromApi(() => api.POST('/api/posts/{slug}/suggestions', { params: { path: { slug } }, body })),
      invalidatesTags: [{ type: 'Suggestion', id: 'LIST' }],
    }),
  }),
})

export const { useSubmitSuggestionMutation } = suggestApi
