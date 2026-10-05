import { api } from '../../api/client'
import type { components } from '../../api/schema'
import { baseApi, fromApi } from '../../services/baseApi'

export type Post = components['schemas']['PostOut']

export const postApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getPost: build.query<Post, string>({
      queryFn: (slug) => fromApi(() => api.GET('/api/posts/{slug}', { params: { path: { slug } } })),
      providesTags: (_r, _e, slug) => [{ type: 'Post', id: slug }],
    }),
  }),
})

export const { useGetPostQuery } = postApi
