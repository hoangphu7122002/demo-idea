import { api } from '../../api/client'
import type { components } from '../../api/schema'
import { baseApi, fromApi } from '../../services/baseApi'
import type { Suggestion } from '../suggest/suggestApi'

export type SuggestionStatus = NonNullable<components['schemas']['SuggestionOut']['status']>
export type RunFilterResult = components['schemas']['RunFilterOut']

export const moderationApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getSuggestions: build.query<Suggestion[], { slug: string; status: SuggestionStatus }>({
      queryFn: ({ slug, status }) => fromApi(() => api.GET('/api/posts/{slug}/suggestions', { params: { path: { slug }, query: { status } } })),
      providesTags: [{ type: 'Suggestion', id: 'LIST' }],
    }),
    runFilter: build.mutation<RunFilterResult, string>({
      queryFn: (slug) => fromApi(() => api.POST('/api/posts/{slug}/run-filter', { params: { path: { slug } } })),
      invalidatesTags: [{ type: 'Suggestion', id: 'LIST' }],
    }),
  }),
})

export const { useGetSuggestionsQuery, useRunFilterMutation } = moderationApi
