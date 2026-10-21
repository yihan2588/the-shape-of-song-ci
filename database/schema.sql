-- Source-controlled schema for the isolated Song Ci Supabase project.
-- Applied remotely with Supabase MCP; migration history is managed by Supabase.
create extension if not exists vector with schema extensions;
create schema if not exists atlas_private;
revoke all on schema atlas_private from public, anon, authenticated;

create table atlas_private.poems (
  position smallint primary key check (position >= 0),
  id text not null unique,
  document jsonb not null,
  tsne jsonb not null check (jsonb_array_length(tsne) = 2),
  umap jsonb not null check (jsonb_array_length(umap) = 2),
  embedding extensions.vector(2560) not null,
  check (document ->> 'id' = id)
);
alter table atlas_private.poems enable row level security;
revoke all on atlas_private.poems from public, anon, authenticated;

create table atlas_private.datasets (
  id text primary key,
  provenance jsonb not null,
  expected_count integer not null check (expected_count > 0)
);
alter table atlas_private.datasets enable row level security;
revoke all on atlas_private.datasets from public, anon, authenticated;

-- Exact float32 cosine scan preserves all 2,560 dimensions. No approximation
-- or half-precision index is needed for a 240-poem corpus.
create function public.song_ci_neighbors(poem_id text)
returns table ("index" integer, cosine double precision)
language sql stable security definer
set search_path = ''
set statement_timeout = '15s'
as $$
  select q.position::integer,
         1 - (p.embedding operator(extensions.<=>) q.embedding) as cosine
  from atlas_private.poems p
  cross join atlas_private.poems q
  where p.id = poem_id and q.id <> p.id
  order by p.embedding operator(extensions.<=>) q.embedding, q.position
  limit 3;
$$;

create function public.get_song_ci_atlas()
returns jsonb
language sql stable security definer
set search_path = ''
set statement_timeout = '15s'
as $$
  select jsonb_build_object(
    'documents', (select jsonb_agg(p.document order by p.position) from atlas_private.poems p),
    'coordinates', jsonb_build_object(
      'tsne', (select jsonb_agg(p.tsne order by p.position) from atlas_private.poems p),
      'umap', (select jsonb_agg(p.umap order by p.position) from atlas_private.poems p)
    ),
    'neighbors', (
      select jsonb_agg(matches.items order by p.position)
      from atlas_private.poems p
      cross join lateral (
        select jsonb_agg(jsonb_build_object('index', n."index", 'cosine', n.cosine)
                         order by n.cosine desc, n."index") as items
        from public.song_ci_neighbors(p.id) n
      ) matches
    ),
    'provenance', (select d.provenance from atlas_private.datasets d where d.id = 'guwendao-v3')
  )
  where (select count(*) from atlas_private.poems) =
        (select d.expected_count from atlas_private.datasets d where d.id = 'guwendao-v3');
$$;

-- The private schema is NOT exposed in PostgREST. Only these read-only RPCs
-- are exposed through the Data API. No role used by the app has write access.
revoke all on function public.song_ci_neighbors(text) from public, anon, authenticated;
revoke all on function public.get_song_ci_atlas() from public, anon, authenticated;
grant execute on function public.song_ci_neighbors(text) to anon, authenticated;
grant execute on function public.get_song_ci_atlas() to anon, authenticated;
