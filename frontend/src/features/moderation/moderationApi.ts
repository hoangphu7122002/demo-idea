import { api } from '../../api/client'
import type { components } from '../../api/schema'
import { baseApi, fromApi } from '../../services/baseApi'
import type { Suggestion } from '../suggest/suggestApi'

export type SuggestionStatus = NonNullable<components['schemas']['SuggestionOut']['status']>
export type RunFilterResult = components['schemas']['RunFilterOut']

export type ApproveResult = components['schemas']['ApproveOut']

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
    approveSuggestion: build.mutation<ApproveResult, number>({
      queryFn: (id) => fromApi(() => api.POST('/api/suggestions/{suggestion_id}/approve', { params: { path: { suggestion_id: id } } })),
      invalidatesTags: [{ type: 'Suggestion', id: 'LIST' }, 'Post'],
    }),
  }),
})

export const { useGetSuggestionsQuery, useRunFilterMutation, useApproveSuggestionMutation } = moderationApi
